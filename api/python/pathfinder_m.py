from math import *
import sbv
import os, sys
import sendEmail

def getMap(filename, idx = (0, 1), sep = '\t', skip = 1):
	authormap = {}
	infile = open(filename, "r")
	while(skip > 0):
		#get the total number of authors/words/confs:
		line = infile.readline()
		skip -= 1

	for line in infile:
		line = line.strip()
		tmp = line.split(sep)
		if len(tmp) > 1:
			mykey = tmp[idx[0]]
			myvalue = tmp[idx[1]]
			#remove prefix
			if "__" in mykey:
				mykey = mykey.split("__")[1]
			if "__" in myvalue:
				myvalue = myvalue.split("__")[1]
			if mykey not in authormap:
				authormap[mykey] = myvalue

	infile.close()
	return authormap

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

def path2pair(pairs, pathline, sep = " ", end = '.'):
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

def getPathScore(pathline, sep = " ", ntopic = 50):
	score = 0
        path1 = "Dicts/"
        mapfile = "authormap.txt"
        probfile = "model-final"+str(ntopic)+".theta_ak"        
	authormap = getMap(path1+mapfile, idx = (0,1), sep = "\t", skip = 1)
	pathline = pathline.strip()
	#print pathline
	tmp = pathline.split(sep)
	i = 0
	n = len(tmp)
	while(i<(n-3)):
		item1 = tmp[i]
		relation = tmp[i+1]
		item2 = tmp[i+2]
		sKL = 50 
               	if item1 in authormap and item2 in authormap:
                      	idx1 = int(authormap[item1])
                      	idx2 = int(authormap[item2])
                      	prob1 = getProbability(idx1, path1+probfile)
                      	prob2 = getProbability(idx2, path1+probfile)
                      	sKL = round(skldivergence(prob1, prob2),3)
			#print idx1, idx2, item1, item2, sKL
		score += sKL
		i += 2

	return score

def rankPath(infile, sep = " ", ntopic = 50):
	mypath = {}
	for line in infile:
		line = line.strip()
		score = getPathScore(line, sep, ntopic)
		if line not in mypath:
			mypath[line] = score	
	return mypath

def getProbability(idx, filename, sep = " "):
        #print filename
        theta_ak = []
        infile = open(filename, "r")
 
        i = 0
        for line in infile:
            if i == idx:
                line = line.strip()
                tmp = line.split(sep)
                #print line
                for item in tmp:
                    item = float(item)
                    theta_ak.append(item)
                break
            i+=1
        #print i
        infile.close()
        return theta_ak

def skldivergence(prob1, prob2, base = 2):
    sKL = 0
    ntopic = len(prob1)
    for i in range(ntopic):
        sKL += (prob1[i]*log(prob1[i]/prob2[i], base)+ prob2[i]*log(prob2[i]/prob1[i], base))
 
    return sKL

def entropy(prob, base = 2):
    sE = 0
    ntopic = len(prob)
    for i in range(ntopic):
        sE -= prob[i]*log(prob[i], base) 
    return sE

def getOccurennceScore(df, df1, df2, N = 18502916, lam = 1, base = e):
	score = log(df*N+lam, base) - log(df1*df2+lam, base)
	return score

def writeDict(D, reverse = True, sep = '\t', n = -1):
	result = []
	i = 0
	if (n < 0):
		n = len(D)

	for (key, value) in sbv.sbv6(D, reverse):
		i += 1
		result.append(str(key)+sep+str(value))
		if i > n:
			break	
	return result

def getBeginEnd(infile):
        line = infile[0]
        line = line.strip()
        tmp = line.split(" ")
        begin = tmp[0]
        end = tmp[-2]
        return (begin, end)

def path2js(infile, n = 20):
	result = []
        (begin, end) = getBeginEnd(infile) 

        nodes = {}
        nodesarr = []
        nodetypes = {}
	i = 0
        for line in infile:
		i += 1
		if i > n and n > 0:
			break
                path = line.split(' ')
                path.pop()
                #print path, len(path)
                for index in range(len(path)):
                        node = path[index]
                        if index % 2 == 0:
                                if not node == end:
                                        if nodes.has_key(node):
                                                neiboughs = nodes[node]
                                                neibough = path[index+1] + "[" + str(index/2) + "]"
                                                neiboughs[neibough] = "1"
                                        else:
                                                neiboughs = {}
                                                neibough = path[index+1] + "[" + str(index/2) + "]"
                                                neiboughs[neibough] = "1"
                                        nodes[node] = neiboughs
                        else:
                                node = node + "[" + str(int(index/2)) + "]"
                                if nodes.has_key(node):
                                        neiboughs = nodes[node]
                                        neiboughs[path[index+1]] = "1"
                                else:
                                        neiboughs = {}
                                        neiboughs[path[index+1]] = "1"
                                nodes[node] = neiboughs
                        nodetypes[node] = index % 2

        node = begin
        nodesarr.append(node)
        index = 0
        record = None
        while True:
                if index >= len(nodesarr):
                        break
                node = nodesarr[index]
                index += 1
                try:
                        sufnode = nodes[node]
                except(KeyError):
                        pass
                for key in sufnode.keys():
                        try:
                                nodesarr.index(key)
                        except(ValueError):
                                if key != end:
                                        nodesarr.append(key)
        nodesarr.append(end)

        #result = open(output, 'w')
        result.append("[")
        for index in range(len(nodesarr)):
                record = "{"
                node = nodesarr[index]
                record += "\"keyword\":\"" + node + "\",\"type\":\"" + str(nodetypes[node]) +"\","
                try:
                        sufnode = nodes[node]
                except(KeyError):
                        pass
                record += "\"links\":["
                for key in sufnode.keys():
                        record += "\"" + key + "\","
                        try:
                                nodesarr.index(key)
                        except(ValueError):
                                nodesarr.append(key)
                record = record[:-1]
                if (index == len(nodesarr) - 1):
                        record += "]}"
                else:
                        record += "]},"
                if record != None:
                        result.append(record)
                
        result.append("]")
        return result

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
		exit(1)
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


def generalSearch(startname, endname, op=2, maxL=3, path2 = "Dicts/Chem2Bio2Rdf/"):
        file1 = "node2id.txt"
        sep1 = " "
        skip1 = 1
        idx1 = (1, 0)
        file2 = "all.txt"
        sep2 = "-->"
        idx2 = (0, 1)
        skip2 = 0
	#print startname, endname
	startid = findNodeID(startname, path2+file1, sep = " ")
	#print startid
	endid = findNodeID(endname, path2+file1, sep=" ")
	#print endid
        commandline =  "./findPath_m "+path2+" "+str(op)+" "+str(startid)+" "+str(endid)+" "+str(maxL)
        print commandline
        
	output1 = os.popen(commandline)
	output2 = reformatePath(output1)
        output1.close()
	#mypath = rankPath(output2, sep = " ", ntopic = 50)
        #output3 = writeDict(mypath, reverse = False, sep = '__', n = len(mypath))
        #output4 = getPathName(output3, path2+file2)
        #output5 = path2js(output4,  n = m)
	return output2

def searchPath(startname, endname, op=2, maxL=3, m = 10, receivers = ['smallerbear@gmail.com','chembiospace@gmail.com']):
	file1 = "node2id.txt"
	sep1 = " "
	skip1 = 1
	idx1 = (1, 0)
	path2 = "Dicts/"
	file2 = "all.txt"
	sep2 = "-->"
	idx2 = (0, 1)
	skip2 = 0
	pathname = "pathfinder/"

	node2id = getMap(path2+file1, idx1, sep1, skip1) 	
	name2node = getMap(path2+file2, idx2, sep2, skip2)
	#print "Ask for start node"
	(startid, startnode) = name2id(name2node, node2id, startname)
	#print "Ask for end node"
	(endid, endnode) = name2id(name2node, node2id, endname)

	commandline =  "./findPath "+str(op)+" "+str(startid)+" "+str(endid)+" "+str(maxL)
	#print commandline
	output1 = os.popen(commandline)
	output2 = reformatePath(output1)
	output1.close()
	mypath = rankPath(output2, sep = " ", ntopic = 50)
	output3 = writeDict(mypath, reverse = False, sep = '__', n = len(mypath))
	output4 = getPathName(output3, path2+file2)
        output5 = path2js(output4,  n = m)
	if len(receivers) > 0:
		title = "Ranked Paths from "+startname+" to "+endname
		body = "*************************\nRanked Paths:\n*************************\n"
		body += "\n".join(output4)
        	body += "\n\n\n*************************\njson.txt:\n*************************\n"
        	body += "\n".join(output5)
		sendEmail.sendEmail(receivers, title, body, sender = 'chembiospaces@gmail.com', usr = 'chembiospaces', password = 'chem2bio2rdf', servername = "smtp.gmail.com", cc = True)
	return output5

if __name__ == "__main__":
	print """
		1 -- test searchPath
		2 -- test generalSearch
	"""
	option = int(raw_input("\nYour Choice: "))
	if option == 1:
	        startname = "Hydrocortisone"
        	endname = "Dexamethasone"
		output5 = searchPath(startname, endname, op=2, maxL=3, m = 10, path2 = "Dicts/Chem2Bio2Rdf/")
		for line in output5:
			print line
	elif option == 2:
		startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5287674"
		endname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/21704"
		result =  generalSearch(startname, endname, op=2, maxL=2, path2 = "Dicts/Chem2Bio2Rdf/")
		print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
		for line in result:
			print line
