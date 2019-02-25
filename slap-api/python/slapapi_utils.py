#!/usr/bin/env python
#############################################################################
#
# Jeremy Yang
# 08 Nov 2014
#############################################################################
import sys,os,re

import slapdb_utils

FINDPATH_EXE="/var/www/html/rest/Chem2Bio2RDF/slap/findPath_m"

#############################################################################
def HTTPErrorExit(code,msg):
  print 'Status: %d %s'%(code,msg)
  print "Content-type: text/plain\n"
  print 'ERROR: (%d) %s'%(code,msg)
  sys.exit(1)

#############################################################################
def GeneralSearch(startid_query, endid_query, op=2, maxL=3, datadir = ""):

  #print startid_query, endid_query
  startid = FindNodeID(startid_query, slapdb_utils.FILE_NODE2ID, sep = " ")
  #print startid
  endid = FindNodeID(endid_query,slapdb_utils.FILE_NODE2ID, sep=" ")
  result=[]

  #if neither start node nor end node is in network, return null
  if (len(endid)==0) :
    result.append(0)
    return result
  if (len(startid)==0) :
    result.append(1)
    return result

  #print endid
  cmd = FINDPATH_EXE+" "+datadir+" "+str(op)+" "+str(startid)+" "+str(endid)+" "+str(maxL)

  output1 = os.popen(cmd)
  output2 = ReformatPath(output1)

  #no path found
  if output2[0]=='.':
    result.append(2)
    return result

  mypath = RankPath(output2, datadir, sep=" ") #weight

  output3 = GetPathPvalue(mypath,datadir) #p value and z score

  z_score=output3[0]

  output4=MakeNetwork(output3[1],0.05)

  if z_score>1212 : #greater than direct+sd
    result.append("very strong")
  elif z_score<=1212 and z_score>128 : #greater than direct
    result.append("strong")
  elif z_score<=128 and z_score>76 : #
    result.append("weak")
  elif z_score<=76 and z_score>38.7 : #smaller than indirect mean+sd
    result.append("very weak")
  elif z_score<=38.7 : #p value <0.05
    result.append("undecided")

  if z_score>0:
    p_value=1.0-sigmoid_normcdflike(log(z_score),mean=1.09,sd=1.56)
  else:
    p_value=1.0

  z_score=round(z_score,2)
  if (p_value>1e-4):
    p_value=round(p_value,4)
  result.append(p_value)
  result.append(z_score)
  result.append(output3[2]) #direct
  result.append(ConvertNetwork2Graphml(startid,endid,output4))
  return result

#############################################################################
def FindNodeID(nodename, filename, sep = " "):
  nodeID = ""
  infile = open(filename, "r")
  for line in infile:
    line = line.strip()
    tmp = line.split(sep)
    if len(tmp) > 1:
      if tmp[1] == nodename:
        nodeID = tmp[0]
        break

  if len(nodeID) == 0:
    print nodename, "not involved in the network. Please try again!"
    #exit(1)
  return nodeID

#############################################################################
def ReformatPath(infile):
  path = ""
  flag = False
  outfile = []

  for line in infile:
    line = line.strip()
    if line == "find ans":
      if path != "":
        outfile.append(path+'.')
      flag = True
      path = ""
    elif flag:
      tmp = line.split(" ")
      path += tmp[1]+" "

  outfile.append(path+".")
  return outfile

#############################################################################
def RankPath(infile, datadir="", sep = " "):
  mypath = {}
  weightMap = GetWeightMap(datadir+"/pair_weight.txt", idx = (0,1), sep = "\t", skip = 1)
  for line in infile:
    line = line.strip()
    score = GetPathScore(weightMap,line, sep)
    if line not in mypath:
      mypath[line] = score
  return mypath

#############################################################################
def GetWeightMap(filename, idx = (0, 1), sep = '\t', skip = 1):
  pathMap = {}
  infile = open(filename, "r")
  for line in infile:
    line = line.strip()
    tmp = line.split(sep)
    if len(tmp) > 1:
      mykey = tmp[0]
      myvalue = tmp[1]
      #remove prefix
      if mykey not in pathMap :
        pathMap [mykey] = myvalue
  infile.close()
  return pathMap

#############################################################################
def GetPathScore(weightMap, pathline, sep = " "):
  result=[]
  score = 0
  pathline = pathline.strip()
  #print pathline
  tmp = pathline.split(sep)
  i = 0
  n = len(tmp)
  weight=0
  weight1=0
  weight2=0
  while(i<(n-3)):
    item1 = tmp[i].split("/")
    item1=item1[len(item1)-1]
    relation = tmp[i+1].split("/")
    #relation = relation[len(relation)-1]
    if relation[len(relation)-1] == "":  #like .. hprd/
      relation= relation[len(relation)-2]
    else:
      relation = relation[len(relation)-1]

    item2 = tmp[i+2].split("/")
    item2 = item2[len(item2)-1]
    path_id1=item1+"$"+relation+"$"+item2
    path_id2=item2+"$"+relation+"$"+item1

    weight_id1=weightMap[path_id1]
    weight_id2=weightMap[path_id2]
    if (weight_id1=="0" or weight_id2=="0"):
      weight=0
      return weight

    if relation == "neighbor":
      weight1=weight1+log(1-(0.7/0.15)*(1-float(weight_id1)))
      weight2=weight2+log(1-(0.7/0.15)*(1-float(weight_id2)))
    else:
      #print(weight_id2)
      weight1=weight1+log(float(weight_id1))
      weight2=weight2+log(float(weight_id2))

    i += 2

  weight=(weight1+weight2)/2
  return weight

#############################################################################
def GetPathPvalue(mypath,datadir=""):
  '''Input pathlist, output my path and it p value.'''
  result = []
  newpath = {}

  expectMeanTable=GetPatternWeightMeanMap(datadir+"/pattern_distribution.txt",sep="\t")
  expectSDTable=GetPatternWeightSDMap(datadir+"/pattern_distribution.txt",sep="\t")

  z_score=0

  #whether direct link, 1: expression, 2 chemogenomics, 0 no direct link
  direct=0
  for key in mypath.keys():
    edges=key.split(" ")
    #if weight smaller than -16, ignore it, go to next path
    if (mypath[key])<-16:
      continue

    #if direct link, break
    if (len(edges)<5):
      if (edges[1]=="http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics"):
        direct=2
      elif (edges[1]=="http://chem2bio2rdf.org/chemogenomics/resource/expression" and direct<2):
        direct=1

    #find pattern
    i=1
    n=len(edges)
    pattern=""
    while(i<n-1):
      pattern=pattern+" "+edges[i]
      i += 2

    #estimate z score
    if pattern in expectMeanTable:
      expected_mean=expectMeanTable[pattern]
      expected_sd=expectSDTable[pattern]
    else:
      expected_mean=-9.2
      expected_sd=2
      print "unexpected pattern"

    #valid path
    if float(mypath[key])> float(expected_mean) and len(edges)>4 :
      z_score=z_score+(float(mypath[key])-float(expected_mean))/float(expected_sd)
      p_value=sigmoid_normcdflike(float(mypath[key]),mean=float(expected_mean),sd=float(expected_sd))
      newpath[key]=1-p_value

  result.append(z_score)
  result.append(newpath)
  result.append(direct)
  return result

#############################################################################
def sigmoid_normcdflike(d, mean, sd):
  '''Sigmoid resembling normal CDF. (JJYang, May 2014)'''
  return ((1.0 + exp(-(1.75/sd)*(d-mean)))**-1)

#############################################################################
def GetPatternWeightMeanMap(filename, sep = '\t'):
  '''Make pattern weight mean hash table.'''
  pathMap = {}
  infile = open(filename, "r")
  for line in infile:
    #line = line.strip()
    tmp = line.split(sep)
    if len(tmp) > 1:
      mykey = tmp[0]
      myvalue = tmp[1]
      #remove prefix
      #print mykey
      if mykey not in pathMap :
        pathMap [mykey] = myvalue

  infile.close()
  return pathMap

#############################################################################
def GetPatternWeightSDMap(filename, sep = '\t'):
  ''Make pattern weight sd  table.'''
  pathMap = {}
  infile = open(filename, "r")
  for line in infile:
    tmp = line.split(sep)
    if len(tmp) > 1:
      mykey = tmp[0]
      myvalue = tmp[2]
      #remove prefix
      if mykey not in pathMap:
        pathMap[mykey] = myvalue
  infile.close()
  return pathMap

#############################################################################
def MakeNetwork(newpath,cutoff=0):
  '''Convert path to network using cutoff.'''
  pairs = {}
  for key in newpath.keys():
    if newpath[key]<cutoff :
      edges=key.split(" ")
      pairs=Path2pair(pairs, key,newpath[key])
  return(pairs)

#############################################################################
def Path2pair(pairs, pathline, sep = " ", end = '.'):
  # nodea relation nodeb relation nodec .
  pathline = pathline.strip()
  #print pathline
  tmp = pathline.split(sep)
  i = 0
  n = len(tmp)
  while(i<(n-3)):
    item1 = tmp[i]
    relation = tmp[i+1]
    item2 = tmp[i+2]
    #print item1, item2, relation
    i += 2
    if (item1, item2) not in pairs:
      pairs[(item1, item2)] = relation
  return pairs

#############################################################################
def ConvertNetwork2Graphml(startname,endname,network):
  '''Convert  network to graphml format.'''
  result="<graphml>"+"\n"
  result=result+"\t"+"<key id=\"label\" for=\"all\" attr.name=\"label\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"class\" for=\"all\" attr.name=\"class\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"uri\" for=\"all\" attr.name=\"uri\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"startnode\" for=\"all\" attr.name=\"startnode\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"evidence\" for=\"all\" attr.name=\"evidence\" attr.type=\"string\"/>"+"\n"
  result=result+"\t"+"<key id=\"weight\" for=\"all\" attr.name=\"weight\" attr.type=\"double\"/>"+"\n"
  result=result+"\t"+"<key id=\"childnodes\" for=\"all\" attr.name=\"childnodes\" attr.type=\"string\"/>"+"\n"

  result=result+"\t"+"<graph edgedefault=\"undirected\">"+"\n"

  nodes = []
  for (node1,node2) in network.keys():
    nodes.append(node1)
    nodes.append(node2)
  nodes=set(nodes)
  for node in nodes:
    result=result+"\t"+"<node id=\""+node+"\">"+"\n"
    strNode=node.split("/")
    
    result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
    result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"
    if node==startname or node==endname:
      result=result+"\t\t"+"<data key=\"startnode\">"+"yes"+"</data>"+"\n"
    else:
      result=result+"\t\t"+"<data key=\"startnode\">"+"no"+"</data>"+"\n"
  
    result=result+"\t"+"</node>"+"\n"

  for (node1,node2) in network.keys():
    result=result+"\t"+"<edge source=\""+node1+"\" target=\""+node2+"\">"+"\n"
    strEdge=network[node1,node2].split("\t")

    #weight
    result=result+"\t\t"+"<data key=\"weight\">"+strEdge[1]+"</data>"+"\n"
    
    #add edge type
    strEdges=strEdge[0].split("/")
    if strEdges[len(strEdges)-1]=="" :
      result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-2]+"</data>"+"\n"
    else:
      result=result+"\t\t"+"<data key=\"label\">"+strEdges[len(strEdges)-1]+"</data>"+"\n"
    
    result=result+"\t\t"+"<data key=\"uri\">"+strEdge[0]+"</data>"+"\n"
    
    #add evidence
    if strEdges[len(strEdges)-1]=="chemogenomics" :
      strNode1=node1.split("/")
      strNode2=node2.split("/")
      #print(strNode2[len(strNode2)-2])
      if strNode2[len(strNode2)-2] == "gene":
        result=result+"\t\t"+"<data key=\"evidence\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode1[len(strNode1)-1]+":"+strNode2[len(strNode2)-1]+"</data>"+"\n"
      else:
        result=result+"\t\t"+"<data key=\"evidence\">"+"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+strNode2[len(strNode2)-1]+":"+strNode1[len(strNode1)-1]+"</data>"+"\n"
    
    result=result+"\t"+"</edge>"+"\n"

  result=result+"\t"+"</graph>"+"\n"
  result=result+"</graphml>"+"\n"
  
  return(result)

