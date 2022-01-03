#!/usr/bin/env python
#############################################################################
# Works via:
#   http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/cid_gene
# with httpd.conf alias:
#   Alias /rest/slap/drug2target /var/www/html/rest/slap/cid_gene.py
# installed
#   vernon:/var/www/html/rest/slap
#
# example:
#   /cid_gene/5591:PPARG
#
# Jeremy Yang
# 
#############################################################################
import sys,os,re,time,json
import cgi

import slapdb_utils
import slapapi_utils

#############################################################################
if __name__=='__main__':

  print "Content-type: text/plain\n\n"

  ### From httpd config.
  SLAPDB_HOST=os.environ['SLAPDB_HOST']
  SLAPDB_NAME=os.environ['SLAPDB_NAME']
  SLAPDB_SCHEMA=os.environ['SLAPDB_SCHEMA']
  SLAPDB_USER=os.environ['SLAPDB_USER']
  SLAPDB_PW=os.environ['SLAPDB_PW']

  dbcon = None
  try:
    dbcon = slapdb_utils.Connect(dbhost=SLAPDB_HOST,dbname=SLAPDB_NAME,dbusr=SLAPDB_USER,dbpw=SLAPDB_PW)
  except Exception,e:
    slapapi_utils.HTTPErrorExit(500,'Database access error: %s'%str(e))

  for envar in (
	'CONTEXT_PREFIX',
	'PATH_INFO',
	'QUERY_STRING'
	):
    print "\t%22s = %s"%('$'+envar,(os.environ[envar] if os.environ.has_key(envar) else ''))

  cid_query, gene_query = os.environ['PATH_INFO'].replace('/','').split(':')
  print "\tDEBUG: cid= %s, gene = %s"%(cid_query,gene_query)

  ### Adapted from prediction1.py:

  cid = slapdb_utils.CheckCompound(dbcon,cid_query)
  gene = slapdb_utils.CheckTarget(dbcon,gene_query)

  if not cid:
    slapapi_utils.HTTPErrorExit(404,'Not found (compound): %s'%cid_query)
  if not gene:
    print 'ERROR: gene not found.'
    slapapi_utils.HTTPErrorExit(404,'Not found (gene): %s'%gene_query)

  print 'DEBUG: compound found: %s -> %s'%(cid_query,cid)
  print 'DEBUG: gene found: %s -> %s'%(gene_query,gene)

  slapapi_utils.HTTPErrorExit(500,'DEBUG: service exit.')

  maxL = 3
  op = 2

  startid = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)
  endid = "http://chem2bio2rdf.org/uniprot/resource/gene/"+gene
  results =  slapapi_utils.GeneralSearch(startid, endid, op, maxL, slapdb_utils.SLAPDATADIR)
  if str(results[0])=="0" :
    print("target was not found")
  elif str(results[0])=="1" :
    print("compound was not found")
  elif str(results[0])=="2" :
    print("no valid path was found")
  else :
    if str(results[3]).strip() == '2':
      type="<a href=\"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+str(cid)+":"+gene+"\">"+"approved binding"+"</a>"
    elif str(results[3]).strip() == '1':
      type="<a href=\"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+str(cid)+":"+gene+"\">"+"approved expression"+"</a>"
    else:
      type="predicted"
      print("<b><i>Input: </i></b> Compound: "+str(cid)+"; Target: "+gene+"\n")
      print("<b><i>P value: </i></b>"+str(results[1])+" ("+str(results[0])+")"+"\n"+"<b><i>Type: </i></b>"+type)
      print("\n*Smaller p value, stronger association\n")
      print(results[4])

