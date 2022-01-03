#!/usr/bin/env python
""" slapdb database utility functions

	Jeremy Yang
"""
import os,sys,re,getopt,cgi,time
import urllib,urllib2
import json
from xml.dom import minidom
import psycopg2
import psycopg2.extras


DBHOST='ec2-54-88-170-209.compute-1.amazonaws.com'
DBNAME='openchord'
DBSCHEMA='c2b2r'
DBUSR='ec2-user'
DBPW='foobar'

SLAPDATADIR='/var/www/html/rest/slap/data'
FILE_TARGET2ID = SLAPDATADIR+"/dicts/target2id.txt"
FILE_NODE2ID = SLAPDATADIR+"/dicts/node2id.txt"
FILE_GENESYMBOLS = SLAPDATADIR+"/dicts/genesymbols.txt"

#############################################################################
def ExeSql(cur,sql):
  try:
    cur.execute(sql)
  except psycopg2.DatabaseError, e:
    print >>sys.stderr,('Postgresql-Error: %s'%e.args)
    return False
  return True

#############################################################################
def Connect(dbhost=DBHOST,dbname=DBNAME,dbusr=DBUSR,dbpw=DBPW):
  """   Connect to database. """
  #dbcon=pgdb.connect(dsn='%s:%s:%s:%s'%(dbhost,dbname,dbusr,dbpw))
  dsn = "host='%s' dbname='%s' user='%s' password='%s'"%(dbhost,dbname,dbusr,dbpw)
  dbcon=psycopg2.connect(dsn)
  dbcon.cursor_factory = psycopg2.extras.RealDictCursor
  return dbcon

#############################################################################
def Info(dbcon,dbschema):
  cur=dbcon.cursor('cursor_unique_name',cursor_factory=psycopg2.extras.RealDictCursor)
  sql=("SELECT table_name FROM information_schema.tables WHERE table_schema IN ('%s','public')"%dbschema)
  ExeSql(cur,sql)
  rows=cur.fetchall()
  return rows

#############################################################################
def DescribeCounts(dbcon,dbschema):
  cur=dbcon.cursor('cursor_unique_name',cursor_factory=psycopg2.extras.RealDictCursor)
  sql=("SELECT table_name FROM information_schema.tables WHERE table_schema IN ('%s','public')"%dbschema)
  ExeSql(cur,sql)
  rows=cur.fetchall()
  outtxt=""
  for row in rows:
    tablename=row[0]
    sql=("SELECT count(*) from %s"%tablename)
    ExeSql(cur,sql)
    row2=cur.fetchone()
    outtxt+="count(%18s): %8d\n"%(tablename,row2[0])
  cur.close()
  return outtxt
  
#############################################################################
def DescribeDB(dbcon,dbschema):
  outtxt=""
  cur=dbcon.cursor('cursor_unique_name',cursor_factory=psycopg2.extras.RealDictCursor)
  sql=("SELECT table_name FROM information_schema.tables WHERE table_schema IN ('%s','public')"%dbschema)
  ExeSql(cur,sql)
  rows=cur.fetchall()
  for row in rows:
    tablename=row[0]
    sql=("SELECT column_name,data_type FROM information_schema.columns WHERE table_name = '%s'"%tablename)
    ExeSql(cur,sql)
    rows2=cur.fetchall()
    outtxt+=("table: %s\n"%tablename)
    for row2 in rows2:
      outtxt+=("\t%s\n"%str(row2))
  cur.close()
  return outtxt

#############################################################################
def CheckCompound(dbcon,cpd):
  '''Parse input compound identifier.  May be CID, name, or smiles.  If not in
knowledge graph, return nearest neighbor via smiles, if possible.'''

  results = []

  ###is CID
  if cpd.isdigit():
    print >>sys.stderr, 'DEBUG: cpd input is CID...'
    return ParseCID(dbcon,cpd)

  ###name or SMILES
  else:
    results=RetrieveCIDsByName(dbcon,cpd)

    if results:
      print >>sys.stderr, 'DEBUG: cpd input is name...'
      for result in results:
        nodeMap = GetNodeID(FILE_TARGET2ID,sep=" ")
        compound_id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(result)
        if compound_id in nodeMap:
          return result #first compound

      return ParseCID(results[0])

    else:
      print >>sys.stderr, 'DEBUG: cpd input should be smiles...'
      results = GetCIDsbySMILES(dbcon,cpd)
      return results[0] if results else ''

#############################################################################
def ParseCID(dbcon,cid):
  '''Either find cpd by CID or nearest neighbor via smiles.'''
  nodeMap = GetNodeID(FILE_TARGET2ID,sep=" ")
  compound_id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)
  if compound_id in nodeMap:
    return cid
  else:
    print >>sys.stderr, 'DEBUG: cpd not found, get nearest neighbor via smiles...'
    results=GetNeighbors(dbcon,GetSMILESByCID(cid))
    return results[0] if results else ''

#############################################################################
def GetNodeID(filename,sep=' '):
  '''Create hash table for nodes.'''
  pathMap = {}
  infile = open(filename, "r")

  for line in infile:
    line = line.strip()
    tmp = line.split(sep)
    if len(tmp) > 1:
      mykey = tmp[1]
      myvalue = tmp[0]
      if mykey not in pathMap :
        pathMap [mykey] = myvalue

  infile.close()
  return pathMap

#############################################################################
def RetrieveCIDsByName(dbcon,name):
  '''Retrieve CID by compound name.'''
  cids = []
  cid=RetrieveCIDsByNameDrugbank(dbcon,name)
  if cid:
    cids.append(cid)
  else:
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pccompound&term=" + name
    dom = minidom.parse(urllib.urlopen(url))
    for node in dom.getElementsByTagName("Id"):
      cids.append(node.childNodes[0].data)
  return cids

#############################################################################
def RetrieveCIDsByNameDrugbank(dbcon,name):
  '''One cid input, one output smiles from pubchem.'''
  cur=dbcon.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  sql=("SELECT cid FROM c2b2r.drugbankdrug WHERE cid IS NOT NULL AND (UPPER(brand) LIKE upper('%"+str(name)+";%') or upper(name) = upper('"+str(name)+"'))")
  ExeSql(cur,sql)
  row=cur.fetchone()
  cur.close()
  return row[0] if row else ''

#############################################################################
def GetNeighbors(dbcon,smi):
  '''Input smiles, get neighbors from c2b2r.'''
  nodeMap = GetNodeID(FILE_TARGET2ID,sep=" ")

  results=[]
  cur = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  sql = ("SELECT cid, tanimoto(gfp, public166keys(keksmiles('"+smi+"')))FROM c2b2r.compound_new WHERE gfpbcnt BETWEEN (nbits_set(public166keys(keksmiles('"+smi+"')))*0.85)::integer AND (nbits_set(public166keys(keksmiles('"+smi+"')))/0.85)::integer AND tanimoto(gfp, public166keys(keksmiles('"+smi+"')))>0.85 ORDER BY tanimoto DESC, cid")
  #sql = "SELECT cid, 1 from  c2b2r_compound_new where cid=5591"
  ExeSql(cur,sql)
  row_count = 0
  for row in cursor:
    #check whether neighbor in slap network
    cid="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(row[0])
    if cid in nodeMap:
      row_count += 1
      results.append(str(row[0])) #+"\t"+str(row[1])
  cur.close()

  return results

#############################################################################
def GetCIDsbySMILES(dbcon,smi):
  '''Input smiles, get CID from c2b2r, not from pubchem. If not, find the
nearest neighbors.

REVISED FOR CLOUD SLAP!  NOW NO INCHI.
'''
  nodeMap = GetNodeID(FILE_TARGET2ID,sep=" ")

  results=[]

  cur = dbcon.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  sql = ("SELECT cid FROM c2b2r.compound_new WHERE cansmi = openbabel.cansmiles('"+smi+"')")

  ExeSql(cur,sql)
  for row in cur:
    #check whether neighbor in slap network
    cid="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(row[0])
    if cid in nodeMap:
      results.append(row[0])
  cur.close()
  if not results:
    results=GetNeighbors(dbcon,smi)

  return results

#############################################################################
def CheckTarget(dbcon,target):
  '''Parse input target identifier.  May be gene symbol, Uniprot, or gene name.'''
  if IsGene(target):
    return target
  results=GetGeneByUniprot(dbcon,target)
  if results!='':
    return results
  results=GetGeneByName(dbcon,target)
  return results[0] if len(results)>0 else ''

#############################################################################
def IsGene(name):
  '''Check whether it is gene symbol.  Gene symbol is derived from c2b2r.chemogenomics
in which # of gene >5; remove single quote'''
  infile = open(FILE_GENESYMBOLS, "r")
  name=name.strip()
  for line in infile:
    if line.strip() == name :
      infile.close()
      return 1
  infile.close()
  return 0

#############################################################################
def GetGeneByName(dbcon,name):
  '''Get gene symbol by name.'''
  results =[]
  cur = dbcon.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  sql = ("SELECT gene_symbol FROM c2b2r.chembl_08_target_dictionary WHERE UPPER(pref_name) = UPPER('"+name+"')")
  ExeSql(cur,sql)
  for row in cur.fetchall():
    results.append(row[0])
  if not results:
    sql = ("SELECT approved_symbol FROM c2b2r.hgnc WHERE UPPER(approved_name) = UPPER('"+name+"')")
    ExeSql(cur,sql)
    for row in cur.fetchall():
      results.append(row[0])
  if not results:
    results=GetGeneByNameNIH(dbcon,name)
  cur.close()
  return results

#############################################################################
def GetGeneByNameNIH(dbcon,name):
  '''get name from NIH protein database.'''
  url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=protein&term=" + name
  dom = minidom.parse(urllib.urlopen(url))
  results = []
  for node in dom.getElementsByTagName("Id"):
    uniprot=''
    gene=''
    gi=node.childNodes[0].data
    gene=GetGeneByGI(dbcon,gi)
    if gene:
      results.append(gene)
      results=list(set(results))
  return results

#############################################################################
def GetGeneByGI(dbcon,gi):
  '''For GI, only consider human from uniprot id mapping.'''
  results = ''
  cur = dbcon.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  sql = ("SELECT genesymbol FROM c2b2r.gi2uniprot,c2b2r.gene2uniprot WHERE c2b2r.gene2uniprot.uniprot=c2b2r.gi2uniprot.uniprot and gi ="+(gi))
  ExeSql(cur,sql)
  for row in cur.fetchall():
    results=row[0]
  cur.close()
  return results

#############################################################################
def GetGeneByUniprot(dbcon,uniprot):
  results = ''
  cur = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  sql = ("SELECT genesymbol FROM c2b2r.gene2uniprot WHERE UPPER(uniprot) = UPPER('"+uniprot+"')")
  ExeSql(cur,sql)
  for row in cur.fetchall():
    results=row[0]
  cur.close()
  return results

#############################################################################
if __name__=='__main__':

  dbcon = Connect()

  rval = Info(dbcon,DBSCHEMA)

  print json.dumps(rval,indent=2)

