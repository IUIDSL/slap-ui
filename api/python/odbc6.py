#!/usr/bin/python
import psycopg2
#note that we have to import the Psycopg2 extras library!
import psycopg2.extras
import sys
import urllib

from xml.dom import minidom

def main():
  #start the script
  #results=getSMILESByCID(208842)
  results=checkCompound("aspirin")

  print results
  return 0

#only output one hit if multiple hits were yielded
def checkCompound(compound):
  results=[]
  #is CID
  if compound.isdigit():
    return parseCID(compound)
  #name or smiles
  else:
    results=retrieveCIDsByName(compound)
    #input is name
    if len(results)>0:
      for result in results:
        file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
        nodeMap = getNodeID(file1,sep = " ")
        compound_id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(result)
        if compound_id in nodeMap:      
          return result #first compound

      #if none of cids in the network, pick the nearest neighbor of the first one
      return parseCID(results[0])
    #input is smiles
    else:
      results=getCIDsbySMILES(compound)
      if len(results)>0:
        return results[0]
      else:
      	return ''

#input is compound id, if cid not in the network, find its nearest neighbor
def parseCID(cid):
  file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
  nodeMap = getNodeID(file1,sep = " ")
  compound_id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)
  if compound_id in nodeMap:
    return cid
  else:
    results=getNeighbors(getSMILESByCID(cid))
    if len(results)>0:
      return results[0] #first nearest neighbor
    else:
      return ''

def checkTarget(target):
  #whether gene symbol
  if isGene(target):
    return target
  #whether uniprot
  results=getGeneByUniprot(target)
  if results!='':
    return results
  #assume gene name
  results=getGeneByName(target)
  if len(results)>0:
    return results[0]
  else:  
    return ''


#check whether it is gene symbol
#gene symbol is derived from c2b2r_chemogenomics in which # of gene >5;remove sigle quote
def isGene(name):
  infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/genesymbols.txt", "r")
  name=name.strip()
  for line in infile:
    if line.strip() == name :
      infile.close()
      return 1
  infile.close()
  return 0 

#get gene symbol by name
def getGeneByName(name):
  results =[]
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT gene_symbol FROM c2b2r_chembl_08_target_dictionary WHERE UPPER(pref_name) = UPPER('"+name+"')")
    for row in cursor:
      results.append(row[0])
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  if len(results)==0:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT \"Approved_Symbol\" FROM \"c2b2r_HGNC\" WHERE UPPER(\"Approved_Name\") = UPPER('"+name+"')")
    for row in cursor:
      results.append(row[0])
    cursor.close()
    conn.close()  
  if len(results)==0:
    results=getGeneByNameNIH(name)
  return results
  
#get name from NIH protein database
def getGeneByNameNIH(name):
  url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=protein&term=" + name
  dom = minidom.parse(urllib.urlopen(url))
  results = []
  for node in dom.getElementsByTagName("Id"):
    uniprot=''
    gene=''
    gi=node.childNodes[0].data
    gene=getGeneByGI(gi)
    if gene !='':  
      results.append(gene)
      results=list(set(results))
  return results

#For GI, only consider human from uniprot id mapping
def getGeneByGI(gi):
  results = ''
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT \"geneSymbol\" FROM \"c2b2r_Gi2UNIPROT_new\",\"c2b2r_GENE2UNIPROT\" WHERE \"c2b2r_GENE2UNIPROT\".uniprot=\"c2b2r_Gi2UNIPROT_new\".uniprot and gi ="+(gi))
    for row in cursor:
      results=row[0]
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return results

def getGeneByUniprot(uniprot):
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  results = ''
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT \"geneSymbol\" FROM \"c2b2r_GENE2UNIPROT\" WHERE UPPER(uniprot) = UPPER('"+uniprot+"')")
    for row in cursor:
      results=row[0]
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return results

#retrieve CID by compound Name
def retrieveCIDsByName(name):
  cids = []
  try:
    cid=retrieveCIDsByNameDrugbank(name)
    if len(cid)<1:
      url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pccompound&term=" + name
      dom = minidom.parse(urllib.urlopen(url))
      for node in dom.getElementsByTagName("Id"):
        cids.append(node.childNodes[0].data)
    else:
      cids.append(cid)
  except:
    pass
  return cids

#one cid input, one output smiles from pubchem
def retrieveCIDsByNameDrugbank(name):
  result=''
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("select cid from c2b2r_drugbankdrug_042011 where cid is not null and (upper(brand) like upper('%"+str(name)+";%') or upper(name) =upper('"+str(name)+"'))")
    for row in cursor:
      result=row[0]
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return result

#create hash table for nodes
def getNodeID(filename, sep = ' '):
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


#input smiles, get CID from c2b2r, not from pubchem. if not, find the nearest neighbors
def getCIDsbySMILES(SMILES):
  file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
  nodeMap = getNodeID(file1,sep = " ")

  url="http://cheminfov.informatics.indiana.edu/rest/format/inchi/SMILES/"+SMILES
  f=urllib.urlopen(url)
  inchi=f.read()
  results=[]
  inchi=inchi.strip()
  #find cid by inchi
  if inchi!='':
    conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
    try:
      conn = psycopg2.connect(conn_string)
      cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
      cursor.execute("SELECT cid FROM c2b2r_compound_new where md5(std_inchi)=md5('"+inchi+"')")
      for row in cursor:
        #check whether neighbor in slap network
        cid="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(row[0])
        if cid in nodeMap:
          results.append(row[0])
      cursor.close()
      conn.close()
    except:
      # Get the most recent exception
      exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
      # Exit the script and print an error telling what happened.
      sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  if len(results)==0:
    results=getNeighbors(SMILES)  

  return results

#one cid input, one output smiles from pubchem
def getSMILESByCID(cid):
  result=''
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT openeye_can_smiles FROM pubchem_compound where cid::INT = ' + str(cid))
    for row in cursor:
      result=row[0]
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return result

#get omim id from disease name
def getOMIMID(disease):
  result=''
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT \"Disease_ID\" from c2b2r_omim_disease where \"Name\"='" + str(disease)+"'")
    for row in cursor:
      result=row[0]
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return result

#input smiles, get neighbors from c2b2r
def getNeighbors(SMILES):
  file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
  nodeMap = getNodeID(file1,sep = " ")

  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  results=[]
  try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    sql = "SELECT cid, tanimoto(gfp, public166keys(keksmiles('" + SMILES + "')))FROM c2b2r_compound_new WHERE gfpbcnt" + " BETWEEN (nbits_set(public166keys(keksmiles('" + SMILES + "'))) * 0.85)::integer" +  " AND (nbits_set(public166keys(keksmiles('" + SMILES + "'))) / 0.85)::integer" +  " AND tanimoto(gfp, public166keys(keksmiles('" + SMILES + "'))) > 0.85 ORDER BY tanimoto DESC, cid"
    #sql = "SELECT cid, 1 from  c2b2r_compound_new where cid=5591"
    cursor.execute(sql)
    row_count = 0
    for row in cursor:
      #check whether neighbor in slap network
      cid="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(row[0])
      if cid in nodeMap:
        row_count += 1
        results.append(str(row[0])) #+"\t"+str(row[1])
    cursor.close()
    conn.close()

  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    print("input "+SMILES+" Database connection failed!\n ->%s" % (exceptionValue))
    return []
  return results

  #results=[]
  #return results #similarity search is not available now

#get target related targets by SEA
def fetchTargetRelatedTargets(gene):
  infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/sea_e_value_1e0.txt", "r")
  targets={}
  results={}
  for line in infile:
    line = line.strip()
    tmp = line.split(" ")
    if tmp[0]==gene:
      targets[tmp[1]]=float(tmp[2])
    elif tmp[1]==gene:
      targets[tmp[0]]=float(tmp[2])
  infile.close()
  if len(targets)>0:
    items = [(v, k) for k, v in targets.items()]
    items.sort()
    items = [(k, v) for v, k in items]
    results=items
  return results

#get gene related compounds
def fetchTargetRelatedCompounds(gene):
  relatedTargets=fetchTargetRelatedTargets(gene)
  relatedTargets=([v for v, k in relatedTargets])
  targets="("
  for target in relatedTargets:
    if len(targets)>1:
      targets=targets+",\'"+target+"\'"
    else:
      targets=targets+"\'"+target+"\'"
  targets=targets+")"

  results=[]
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  # print the connection string we will use to connect
  try:
    conn = psycopg2.connect(conn_string)

    # HERE IS THE IMPORTANT PART, by specifying a name for the cursor
    # psycopg2 creates a server-side cursor, which prevents all of the
    # records from being downloaded at once from the server.
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT \"CID\" FROM c2b2r_chemogenomics where primary_source!=\' CTD \' and med_interested=1 and \"GENE\" in '+targets+' limit 500')

    # This loop should run 1000 times, assuming there are at least 1000
    # records in 'my_table'
    row_count = 0
    for row in cursor:
      row_count += 1
      results.append(str(row[0]))
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return(results)

#get gene related compounds
def fetchTargetLigands(gene):
  results=[]
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  # print the connection string we will use to connect
  try:
    conn = psycopg2.connect(conn_string)

    # HERE IS THE IMPORTANT PART, by specifying a name for the cursor
    # psycopg2 creates a server-side cursor, which prevents all of the
    # records from being downloaded at once from the server.
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT \"CID\",openeye_can_smiles,primary_source FROM c2b2r_chemogenomics,c2b2r_compound_new where c2b2r_chemogenomics.\"CID\"=c2b2r_compound_new.cid and primary_source!=\' CTD \' and med_interested=1 and \"GENE\"=\''+gene+'\'')

    # This loop should run 1000 times, assuming there are at least 1000
    # records in 'my_table'
    row_count = 0
    for row in cursor:
      row_count += 1
      results.append(str(row[0])+"\t"+row[2]+"\t"+row[1])
    cursor.close()
    conn.close()
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
  return(results)

#input and cids, which are the neighbors of input
def cidNetworks(input,cids):
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  # print the connection string we will use to connect

  result="<graphml>"+"\n"
  result=result+"\t"+"<key id=\"label\" for=\"all\" attr.name=\"label\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"class\" for=\"all\" attr.name=\"class\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"uri\" for=\"all\" attr.name=\"uri\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"startnode\" for=\"all\" attr.name=\"startnode\" attr.type=\"string\"/>"+"\n"

  result=result+"\t"+"<graph edgedefault=\"undirected\">"+"\n"

  #add edge from input to cids
  for cid in cids:
    node1="http://chem2bio2rdf.org/"+str(input)
    node2="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)
    result=result+"\t"+"<edge source=\""+node1+"\" target=\""+node2+"\">"+"\n"
    result=result+"\t\t"+"<data key=\"label\">"+"neighbor"+"</data>"+"\n"    
    result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/pubchem/resource/neighbor/"+"</data>"+"\n"
    result=result+"\t"+"</edge>"+"\n"

  #add edge from cid to genes
  genes=[] #all cid genes
  for cid in cids:
    try:
      conn = psycopg2.connect(conn_string)
      cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
      cursor.execute('SELECT \"GENE\" FROM c2b2r_chemogenomics where primary_source!=\' CTD \' and med_interested=1 and \"CID\"=' + str(cid))
      row_count = 0
      for row in cursor:
        row_count += 1
        genes.append(row[0])

        #add edge
        node1="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)        
        node2="http://chem2bio2rdf.org/uniprot/resource/gene/"+row[0]

        result=result+"\t"+"<edge source=\""+node1+"\" target=\""+node2+"\">"+"\n"
        strEdge="http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics"
        strEdges=strEdge.split("/")
        if strEdges[len(strEdges)-1]=="" :
          result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-2]+"</data>"+"\n"
        else:
          result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-1]+"</data>"+"\n"
      
        if strEdges[len(strEdges)-1]=="chemogenomics" :
          strNode1=node1.split("/")
          strNode2=node2.split("/")
          #print(strNode2[len(strNode2)-2])
          if strNode2[len(strNode2)-2] == "gene":
            result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode1[len(strNode1)-1]+":"+strNode2[len(strNode2)-1]+"</data>"+"\n"
          else:
            result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode2[len(strNode2)-1]+":"+strNode1[len(strNode1)-1]+"</data>"+"\n"
        else :
          result=result+"\t\t"+"<data key=\"uri\">"+strEdge+"</data>"+"\n"
    
        result=result+"\t"+"</edge>"+"\n"
    except:
      # Get the most recent exception
      exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
      # Exit the script and print an error telling what happened.
      sys.exit("Database connection failed!\n ->%s" % (exceptionValue))

  #add nodes
  #add input:
  node="http://chem2bio2rdf.org/"+str(input)
  result=result+"\t"+"<node id=\""+node+"\">"+"\n"
  result=result+"\t\t"+"<data key=\"label\">"+str(input)+"</data>"+"\n"
  result=result+"\t\t"+"<data key=\"class\">"+"pubchem_compound"+"</data>"+"\n"
  result=result+"\t\t"+"<data key=\"startnode\">"+"yes"+"</data>"+"\n"
  result=result+"\t"+"</node>"+"\n"

  #cids
  for cid in cids:
    node = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)    
    result=result+"\t"+"<node id=\""+node+"\">"+"\n"
    strNode=node.split("/")    
    result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"startnode\">"+"no"+"</data>"+"\n"
    result=result+"\t"+"</node>"+"\n"

  #genes
  genes=list(set(genes))
  for gene in genes:
    node = "http://chem2bio2rdf.org/uniprot/resource/gene/"+gene
    result=result+"\t"+"<node id=\""+node+"\">"+"\n"
    strNode=node.split("/")    
    result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"startnode\">"+"no"+"</data>"+"\n"
    result=result+"\t"+"</node>"+"\n"

  result=result+"\t"+"</graph>"+"\n"
  result=result+"</graphml>"+"\n"
  
  return(result)

def cidNetwork(cid):
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  # print the connection string we will use to connect
  print "Connecting to database\n  ->%s" % (conn_string)

  try:
    conn = psycopg2.connect(conn_string)

    # HERE IS THE IMPORTANT PART, by specifying a name for the cursor
    # psycopg2 creates a server-side cursor, which prevents all of the
    # records from being downloaded at once from the server.
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT \"GENE\" FROM c2b2r_chemogenomics where primary_source!=\' CTD \' and med_interested=1 and \"CID\"=' + str(cid))

    # Because cursor objects are iterable we can just call 'for - in' on
    # the cursor object and the cursor will automatically advance itself
    # each iteration.
    # This loop should run 1000 times, assuming there are at least 1000
    # records in 'my_table'
    row_count = 0
    genes=[]
    for row in cursor:
      row_count += 1
      genes.append(row[0])
    return(convertNetwork2GraphmlByCID(str(cid),genes))
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))

#convert  network to graphml format
def convertNetwork2GraphmlByCID(cid, network):
  result="<graphml>"+"\n"
  result=result+"\t"+"<key id=\"label\" for=\"all\" attr.name=\"label\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"class\" for=\"all\" attr.name=\"class\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"uri\" for=\"all\" attr.name=\"uri\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"startnode\" for=\"all\" attr.name=\"startnode\" attr.type=\"string\"/>"+"\n"

  result=result+"\t"+"<graph edgedefault=\"undirected\">"+"\n"

  node = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+cid
  result=result+"\t"+"<node id=\""+node+"\">"+"\n"
  strNode=node.split("/")
    
  result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
  result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
  result=result+"\t\t"+"<data key=\"startnode\">"+"yes"+"</data>"+"\n"

  result=result+"\t"+"</node>"+"\n"

  for row in network:
    node = "http://chem2bio2rdf.org/uniprot/resource/gene/"+row
    result=result+"\t"+"<node id=\""+node+"\">"+"\n"
    strNode=node.split("/")
    
    result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"startnode\">"+"no"+"</data>"+"\n"

    result=result+"\t"+"</node>"+"\n"

  for row in network:
    node1="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+cid
    node2="http://chem2bio2rdf.org/uniprot/resource/gene/"+row

    result=result+"\t"+"<edge source=\""+node1+"\" target=\""+node2+"\">"+"\n"
    strEdge="http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics"
    strEdges=strEdge.split("/")
    if strEdges[len(strEdges)-1]=="" :
      result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-2]+"</data>"+"\n"
    else:
      result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-1]+"</data>"+"\n"
      
    if strEdges[len(strEdges)-1]=="chemogenomics" :
      strNode1=node1.split("/")
      strNode2=node2.split("/")
      #print(strNode2[len(strNode2)-2])
      if strNode2[len(strNode2)-2] == "gene":
        result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode1[len(strNode1)-1]+":"+strNode2[len(strNode2)-1]+"</data>"+"\n"
      else:
        result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode2[len(strNode2)-1]+":"+strNode1[len(strNode1)-1]+"</data>"+"\n"
    else :
      result=result+"\t\t"+"<data key=\"uri\">"+strEdge+"</data>"+"\n"
    
    result=result+"\t"+"</edge>"+"\n"

  result=result+"\t"+"</graph>"+"\n"
  result=result+"</graphml>"+"\n"
  
  return(result)

def geneNetwork(gene):
  conn_string = "host='localhost' dbname='chord' user='cicc3' password=''"
  # print the connection string we will use to connect
  print "Connecting to database\n  ->%s" % (conn_string)
  try:
    conn = psycopg2.connect(conn_string)

    # HERE IS THE IMPORTANT PART, by specifying a name for the cursor
    # psycopg2 creates a server-side cursor, which prevents all of the
    # records from being downloaded at once from the server.
    cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT \"CID\" FROM c2b2r_chemogenomics where primary_source!=\' CTD \' and med_interested=1 and \"GENE\"=\''+gene+'\' limit 100')

    # Because cursor objects are iterable we can just call 'for - in' on
    # the cursor object and the cursor will automatically advance itself
    # each iteration.
    # This loop should run 1000 times, assuming there are at least 1000
    # records in 'my_table'
    row_count = 0
    cids=[]
    for row in cursor:
      row_count += 1
      cids.append(row[0])
    return(convertNetwork2GraphmlByGene(gene,cids))
  except:
    # Get the most recent exception
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    # Exit the script and print an error telling what happened.
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))

#convert  network to graphml format
def convertNetwork2GraphmlByGene(gene, network):
  result="<graphml>"+"\n"
  result=result+"\t"+"<key id=\"label\" for=\"all\" attr.name=\"label\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"class\" for=\"all\" attr.name=\"class\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"uri\" for=\"all\" attr.name=\"uri\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"startnode\" for=\"all\" attr.name=\"startnode\" attr.type=\"string\"/>"+"\n"

  result=result+"\t"+"<graph edgedefault=\"undirected\">"+"\n"

  node = "http://chem2bio2rdf.org/uniprot/resource/gene/"+gene
  result=result+"\t"+"<node id=\""+node+"\">"+"\n"
  strNode=node.split("/")
    
  result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
  result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
  result=result+"\t\t"+"<data key=\"startnode\">"+"yes"+"</data>"+"\n"

  result=result+"\t"+"</node>"+"\n"

  for row in network:
    node = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(row)
    result=result+"\t"+"<node id=\""+node+"\">"+"\n"
    strNode=node.split("/")
    
    result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"startnode\">"+"no"+"</data>"+"\n"

    result=result+"\t"+"</node>"+"\n"

  for row in network:
    node1="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(row)
    node2="http://chem2bio2rdf.org/uniprot/resource/gene/"+gene

    result=result+"\t"+"<edge source=\""+node1+"\" target=\""+node2+"\">"+"\n"
    strEdge="http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics"
    strEdges=strEdge.split("/")
    if strEdges[len(strEdges)-1]=="" :
      result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-2]+"</data>"+"\n"
    else:
      result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-1]+"</data>"+"\n"
      
    if strEdges[len(strEdges)-1]=="chemogenomics" :
      strNode1=node1.split("/")
      strNode2=node2.split("/")
      #print(strNode2[len(strNode2)-2])
      if strNode2[len(strNode2)-2] == "gene":
        result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode1[len(strNode1)-1]+":"+strNode2[len(strNode2)-1]+"</data>"+"\n"
      else:
        result=result+"\t\t"+"<data key=\"uri\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode2[len(strNode2)-1]+":"+strNode1[len(strNode1)-1]+"</data>"+"\n"
    else :
      result=result+"\t\t"+"<data key=\"uri\">"+strEdge+"</data>"+"\n"
    
    result=result+"\t"+"</edge>"+"\n"

  result=result+"\t"+"</graph>"+"\n"
  result=result+"</graphml>"+"\n"
  
  return(result)

#main()
