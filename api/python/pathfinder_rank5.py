from math import *
import sbv
import os, sys
import sendEmail
#import rpy2.robjects as robjects


#############################################################################
def sigmoid_normcdflike(d, mean, sd):
  '''Sigmoid resembling normal CDF. (JJYang, May 2014)'''
  return ((1.0 + exp(-(1.75/sd)*(d-mean)))**-1)


def getWeightMap(filename, idx = (0, 1), sep = '\t', skip = 1):
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

#make pattern weight mean hash table
def getPatternWeightMeanMap(filename, sep = '\t'):
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

#make pattern weight sd  table
def getPatternWeightSDMap(filename, sep = '\t'):
	pathMap = {}
	infile = open(filename, "r")

	for line in infile:
		#line = line.strip()
		tmp = line.split(sep)
		if len(tmp) > 1:
			mykey = tmp[0]
			myvalue = tmp[2]
			#remove prefix
			if mykey not in pathMap :
				pathMap [mykey] = myvalue

	infile.close()
	return pathMap 

def reformatePath(infile):
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

def path2pair(pairs, pathline,score, sep = " "):
	# the value of pairs combines the relation and the min p value involoved.
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
			pairs[(item1, item2)] = relation+"\t"+str(score)
		else:
			temp=pairs[(item1, item2)].split("\t")
			#min score is used for the edge
			if float(score)<float(temp[1]):
				pairs[(item1, item2)] = relation+"\t"+str(score)		
        return pairs

def path2network(pathfile, networkfile):
        infile = open(pathfile, "r")
        outfile = open(networkfile, "w")
        pairs = {}
        for line in infile:
                pairs = path2pair(pairs, line)

        for key in pairs:
                outfile.write('\t'.join(key)+'\t'+pairs[key]+'\n')
        infile.close()
        outfile.close()

def getDict(filename, sep = "-->"):
	mydict = {}
	infile = open(filename, "r")
	
	for line in infile:
		line = line.strip()
		tmp = line.split(sep)
		if len(tmp) > 1:
			itemname = tmp[0]
			item = tmp[1]
			(itemtype, itemid) = item.split("__")
			if itemid not in mydict:
				mydict[itemid] = (itemname, itemtype)
	infile.close()
	return mydict

def getNode(networkfile):
	nodes = []
	infile = open(networkfile, "r")
	for line in infile:
		line = line.strip()
		tmp = line.split('\t')
		if len(tmp) > 1:
			item1 = tmp[0]
			item2 = tmp[1]
			if item1 not in nodes:
				nodes.append(item1)
			if item2 not in nodes:
				nodes.append(item2)

	infile.close()
	return nodes

def node2file(nodes, nodefile, dictfile):
	mydict = getDict(dictfile)
	outfile = open(nodefile, "w")
	for item in nodes:
		(itemname, itemtype) = (item, "unknown")
		if item in mydict:
			(itemname, itemtype) = mydict[item]
		outfile.write(item+'\t'+itemname+'\t'+itemtype+'\n')
	outfile.close()

def network2node(networkfile, nodefile, dictfile):
	nodes = getNode(networkfile)
	node2file(nodes, nodefile, dictfile)

def getPathName(infile, dictfile):
	mydict = getDict(dictfile)
	outfile = []
	for line in infile:
		re = ""
		line = line.strip()
		tmp = line.split(" ")
		if len(tmp) > 1:
			for i in range(0, len(tmp), 2):
				item = tmp[i]
				relation = tmp[i+1]
				if item in mydict:
					item = mydict[item][0].strip()
					#avoid long name
					x = item.split(" ")
					if len(x) > 3:
						item = "-".join(x[:3])
					elif len(x) > 1:
						item = "-".join(x)
				if i < (len(tmp)-2):
					re += item+" "+relation+" "
				else:
					re += item+ " "+relation
			outfile.append(re)
	return outfile


def getPathName_m(infile, dictfile):
	mydict = getDict(dictfile)
	outfile = []
	for line in infile:
		re = ""
		line = line.strip()
		tmp = line.split(" ")
		if len(tmp) > 1:
			for i in range(0, len(tmp), 2):
				item = tmp[i]
				relation = tmp[i+1]
				if item in mydict:
					itemname = mydict[item][0].strip()
					itemtype = mydict[item][1].strip()
					#avoid long name
					x = itemname.split(" ")
					if len(x) > 3:
						itemname = "-".join(x[:3])
					elif len(x) > 1:
						itemname = "-".join(x)
				else:
					itemname = "*"
					itemtype = "*"
				newitem = itemtype+"__"+item+":"+itemname
				if i < (len(tmp)-2):
					re += newitem+" "+relation+" "
				else:
					re += newitem+ " "+relation
			outfile.append(re)
	return outfile

def getPathScore(weightMap, pathline, sep = " "):
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

def rankPath(infile, path2="", sep = " "):
	mypath = {}
	weightMap = getWeightMap(path2+"Dicts/pair_weight.txt", idx = (0,1), sep = "\t", skip = 1)

	for line in infile:
		line = line.strip()       	
		score = getPathScore(weightMap,line, sep)
		if line not in mypath:
			mypath[line] = score	
	return mypath

#for batch drug target prediction, read weightMap outside
def rankPath2(weightMap,infile, path2="", sep = " "):
	mypath = {}

	for line in infile:
		line = line.strip()       	
		score = getPathScore(weightMap,line, sep)
		if line not in mypath:
			mypath[line] = score	
	return mypath

def writeDict(D, reverse = True, sep = '\t', n = -1):
	result = []
	i = 0
	if (n < 0):
		n = len(D)

	for (key, value) in sbv.sbv0(D,reverse):
		i += 1
		result.append(str(value)+sep+str(key))
		if i > n:
			break	
	return result

#input pathlist, output my path and it p value
def getPathPvalue(mypath,path2=""):
	result = []
	newpath = {}
	#r = robjects.r

	expectMeanTable=getPatternWeightMeanMap(path2+"Dicts/pattern_distribution.txt",sep="\t")
	expectSDTable=getPatternWeightSDMap(path2+"Dicts/pattern_distribution.txt",sep="\t")

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

			#newpath = {} #reinitiate 
			#newpath[key]=0

			#z_score=1000 #default, very high confidence
			#break

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

			#p_value=r.pnorm(float(mypath[key]),mean=float(expected_mean),sd=float(expected_sd))
			#newpath[key]=1-p_value[0]

			p_value=sigmoid_normcdflike(float(mypath[key]),mean=float(expected_mean),sd=float(expected_sd))
			newpath[key]=1-p_value

	result.append(z_score)
	result.append(newpath)
	result.append(direct)
	return result

#convert path to network using cutoff
def makeNetwork(newpath,cutoff=0):
	pairs = {}
	for key in newpath.keys():
		if newpath[key]<cutoff :
			edges=key.split(" ")
			pairs=path2pair(pairs, key,newpath[key])
	return(pairs)

def convertNetwork2Graphml(startname,endname,network):
	nodeNeighbors={}
	#node neighbors
	for (node1,node2) in network.keys():
		if node1 in nodeNeighbors.keys():
			nodeNeighbors[node1]=nodeNeighbors[node1]+"\t"+node2
		else:
			nodeNeighbors[node1]=node2

		if node2 in nodeNeighbors.keys():
			nodeNeighbors[node2]=nodeNeighbors[node2]+"\t"+node1
		else:
			nodeNeighbors[node2]=node1		

	#find parents
	nodeParents={}
	nodeChildren={}

	for i in range(1,len(nodeNeighbors.keys())):
		node1=nodeNeighbors.keys()[i-1]
		neighbors1=nodeNeighbors[node1].split("\t").sort()
		class1=node1.split("/")
		class1=class1[len(class1)-2]

		#only node with 2 neighbors have parent; and node could not be grandparent
		if nodeNeighbors[node1].count("\t")==1 and node1!=startname and node1 !=endname and node1 not in nodeParents.keys():
			#find other nodes
			for j in range(i+1,len(nodeNeighbors.keys())+1):
				node2=nodeNeighbors.keys()[j-1]
				if nodeNeighbors[node2].count("\t")==1  and node2!=startname and node2 !=endname:
					class2=node2.split("/")
					class2=class2[len(class2)-2]
					#same class
					if class1==class2:
						neighbors1=sorted(nodeNeighbors[node1].split("\t"))
						neighbors2=sorted(nodeNeighbors[node2].split("\t"))

						#same neighbors
						if "".join(neighbors1)=="".join(neighbors2):
							#consider node1 is the parent of node2 
							nodeParents[node2]=node1
			
							#node 2 is the child of node1
							if node1 in nodeChildren.keys():
								nodeChildren[node1]=nodeChildren[node1]+"\t"+node2
							else:
								nodeChildren[node1]=node2

	#if node has no child and itself is not a child
	for node in nodeNeighbors.keys():
		if node not in nodeParents.keys() and node not in nodeChildren.keys():
			nodeChildren[node]=node	
						
	nodes=nodeNeighbors.keys()

	#convert  network to graphml format
	result="<graphml>"+"\n"
	result=result+"\t"+"<key id=\"label\" for=\"all\" attr.name=\"label\" attr.type=\"string\"/>"+"\n"
	result=result+"\t"+"<key id=\"class\" for=\"all\" attr.name=\"class\" attr.type=\"string\"/>"+"\n"
	result=result+"\t"+"<key id=\"uri\" for=\"all\" attr.name=\"uri\" attr.type=\"string\"/>"+"\n"
	result=result+"\t"+"<key id=\"startnode\" for=\"all\" attr.name=\"startnode\" attr.type=\"string\"/>"+"\n"
	result=result+"\t"+"<key id=\"evidence\" for=\"all\" attr.name=\"evidence\" attr.type=\"string\"/>"+"\n"
	result=result+"\t"+"<key id=\"weight\" for=\"all\" attr.name=\"weight\" attr.type=\"double\"/>"+"\n"
	result=result+"\t"+"<key id=\"childnodes\" for=\"all\" attr.name=\"childnodes\" attr.type=\"string\"/>"+"\n"
	result=result+"\t"+"<key id=\"nodesize\" for=\"all\" attr.name=\"nodesize\" attr.type=\"double\"/>"+"\n"

	result=result+"\t"+"<graph edgedefault=\"undirected\">"+"\n"

	#only show the nodes which are parents
	for node in nodeChildren.keys():
		result=result+"\t"+"<node id=\""+node+"\">"+"\n"
		strNode=node.split("/")

		children_number=0
		if nodeChildren[node]!=node:
			result=result+"\t\t"+"<data key=\"childnodes\">"+nodeChildren[node]+"</data>"+"\n"	
			children_number=nodeChildren[node].count("\t")+1	
			result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"("+str(children_number)+")"+"</data>"+"\n"
		else:
			result=result+"\t\t"+"<data key=\"label\">"+strNode[len(strNode)-1]+"</data>"+"\n"
		
		result=result+"\t\t"+"<data key=\"class\">"+strNode[len(strNode)-2]+"</data>"+"\n"

		if node==startname or node==endname:
			result=result+"\t\t"+"<data key=\"nodesize\">"+"5"+"</data>"+"\n"
		elif children_number>0:
			result=result+"\t\t"+"<data key=\"nodesize\">"+"3"+"</data>"+"\n"
		else:
			result=result+"\t\t"+"<data key=\"nodesize\">"+"1"+"</data>"+"\n"
							
		if node==startname or node==endname:
			result=result+"\t\t"+"<data key=\"startnode\">"+"yes"+"</data>"+"\n"
		else:
			result=result+"\t\t"+"<data key=\"startnode\">"+"no"+"</data>"+"\n"
	
		result=result+"\t"+"</node>"+"\n"

	for (node1,node2) in network.keys():
		if node1 not in nodeChildren.keys() or node2 not in nodeChildren.keys():
			continue
		
		strEdge=network[node1,node2].split("\t")
		weight=float(strEdge[1])

		# if child weight<parent node, give to parent node. We wanna this edge weight to be minimum so that will not be filtered out 
		if node1 in nodeChildren.keys():
			for child in nodeChildren[node1].split("\t"):
				tempWeight=float(network[child,node2].split("\t")[1])
				if tempWeight<weight:
					weight=tempWeight

		if node2 in nodeChildren.keys():
			for child in nodeChildren[node2].split("\t"):
				#print node2+"\t"+child+"\t"+node1
				tempWeight=float(network[node1,child].split("\t")[1])
				if tempWeight<weight:
					weight=tempWeight
				
		result=result+"\t"+"<edge source=\""+node1+"\" target=\""+node2+"\">"+"\n"

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

#convert  network to graphml format
def convertNetwork2Graphml_old(startname,endname,network):
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

def findNodeID(nodename, filename, sep = " "):
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

def name2id(name2node, node2id, startname):
        startid = ""
	startnode = ""
        if startname in name2node.keys():
        	startnode = name2node[startname]
        elif startname in name2node.values():
        	startnode = startname
        else:
        	print "Node not find!"
                        

	if startnode in node2id and startnode != "":
        	startid = node2id[startnode]
        else:
        	print "Node not in the network!"

	return (startid, startnode)

#for batch drug target prediction, read weight map outside, only retrieve p value and z score
def retrieveScore(weightMap,startid, endid, op=2, maxL=3, path2 = ""):
	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/node2id.txt"

	result=[]

	#print endid
        commandline =  "/var/www/html/rest/Chem2Bio2RDF/slap/findPath_m "+path2+"Dicts/"+" "+str(op)+" "+str(startid)+" "+str(endid)+" "+str(maxL)
        
	output1 = os.popen(commandline)
	output2 = reformatePath(output1)

	#no path found
	if output2[0]=='.':
		result.append(0) #z score
		result.append(1) # p value
		result.append(0)
		return result

	mypath = rankPath2(weightMap,output2, path2, sep=" ") #weight

	output3 = getPathPvalue(mypath,path2) #p value and z score
	z_score=output3[0]
	if z_score>0:
		#r = robjects.r
		#p_value=1.0-r.pnorm(log(z_score),mean=1.09,sd=1.56)[0]
		p_value=1.0-sigmoid_normcdflike(log(z_score),mean=1.09,sd=1.56)
	else:
		p_value=1.0

	z_score=round(z_score,2)
	if (p_value>1e-4):
		p_value=round(p_value,4)

	result.append(z_score)
	result.append(p_value)
	result.append(output3[2])
	return result

def generalSearch(startname, endname, op=2, maxL=3, path2 = ""):
	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/node2id.txt"

	#print startname, endname
	startid = findNodeID(startname, file1, sep = " ")
	#print startid
	endid = findNodeID(endname,file1, sep=" ")
	result=[]

	#if neither start node nor end node is in network, return null
	if (len(endid) ==0) :
		result.append(0)
		return result
	if (len(startid) ==0) :
		result.append(1)
		return result

	#print endid
        commandline =  "/var/www/html/rest/Chem2Bio2RDF/slap/findPath_m "+path2+"Dicts/"+" "+str(op)+" "+str(startid)+" "+str(endid)+" "+str(maxL)
        
	output1 = os.popen(commandline)
	output2 = reformatePath(output1)

	#no path found
	if output2[0]=='.':
		result.append(2)
		return result

	mypath = rankPath(output2, path2, sep=" ") #weight

	#mypath = sbv.sbv0(mypath,reverse =True) #order the paths based on weight

	output3 = getPathPvalue(mypath,path2) #p value and z score

	z_score=output3[0]

	#if z_score>1000 :
		#output4=makeNetwork(output3[1],0.01)
	#elif z_score>100 :
		#output4=makeNetwork(output3[1],0.2)
	#else:
	
	output4=makeNetwork(output3[1],0.05)

	if z_score>1212 : #greter than direct+sd
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
		#r = robjects.r
		#p_value=1.0-r.pnorm(log(z_score),mean=1.09,sd=1.56)[0]
		p_value=1.0-sigmoid_normcdflike(log(z_score),mean=1.09,sd=1.56)
	else:
		p_value=1.0

	z_score=round(z_score,2)
	if (p_value>1e-4):
		p_value=round(p_value,4)
	result.append(p_value)
	#result.append(output3[1]) 
	result.append(z_score) 
	result.append(output3[2]) #direct
	result.append(convertNetwork2Graphml(startname,endname,output4))
	return result


def generalSearchBatchCIDs(originalStartName, startnames, originalEndName,endname, op=2, maxL=3, path2 = ""):

	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/node2id.txt"

	endid = findNodeID(endname, file1, sep=" ")
	result=[]
	paths = {}
	z_score = 0
	validPath=0

	if len(endid) ==0 :
		result.append(0)
		return result
	
	for startname in startnames:
		#print startname, endname
		startid = findNodeID(startname, file1, sep = " ")
	
		#if start node is not in the network, go to next start id
		if len(startid) ==0  :
			continue

        	commandline =  "."+path2+"/findPath_m "+path2+"Dicts/"+" "+str(op)+" "+str(startid)+" "+str(endid)+" "+str(maxL)
        
		output1 = os.popen(commandline)
		output2 = reformatePath(output1)

		#no path found, go to next start id
		if output2[0]=='.':
			continue

		mypath = rankPath(output2, path2, sep = " ") #weight

		output3 = getPathPvalue(mypath, path2) #p value and z score

		#append paths
		for key in output3[1].keys() :
			newkey = " "+originalname+" "+"http://chem2bio2rdf.org/pubchem/resource/neighbor"+" "+key
			paths[newkey] = output3[1][key]
		validPath = validPath +1
		z_score=z_score+output3[0]

	#print(paths)
	if validPath>0 :
		z_score=z_score/validPath
	else:
		result.append(2)
		return result

	output4=makeNetwork(paths,0.01)

	if z_score>1212 : #greter than direct+sd
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
		#r = robjects.r
		#p_value=1.0-r.pnorm(log(z_score),mean=1.09,sd=1.56)[0]
		p_value=1.0-sigmoid_normcdflike(log(z_score),mean=1.09,sd=1.56)
	else:
		p_value=1.0

	result.append(p_value)
	result.append(convertNetwork2Graphml(originalname,endname,output4))
	result.append(output3[1])
	result.append(z_score)
	result.append(0) #undirect link
	return result

