#!/usr/bin/env python
import pathfinder_rank5
import math, sys, time, os
import pp
import random
import odbc6

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

def predict(inputFile,step,maxLineNumber,needPreprocess):
#inputFile: the pair file; step: interval; maxLineNumber: used for separate groups
	baseFile="/var/lib/tomcat/webapps/slap/temp/"

	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
	weightMap = pathfinder_rank5.getWeightMap("/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/pair_weight.txt", idx = (0,1), sep = "\t", skip = 1)
	nodeMap = getNodeID(file1,sep = " ")

	infile = open(baseFile+inputFile, "r")
	lineNumber=0
	results=[]
	for line in infile:
		line = line.strip()
		lineNumber +=1

		if (lineNumber>maxLineNumber-step and lineNumber<=maxLineNumber) :
			nodes=line.split("\t")
			cid=nodes[0]
			gene=nodes[1]
			if needPreprocess==1:
				cid=odbc6.checkCompound(nodes[0])
				gene=odbc6.checkTarget(nodes[1])

			endname = "http://chem2bio2rdf.org/uniprot/resource/gene/" + gene
			startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(cid)
			if endname in nodeMap:
				endid = nodeMap[endname]
			else:
				results.append(str(nodes[0])+"\t"+nodes[1]+"\t"+"NA"+"\t"+"NA"+"\t"+"no matched target")	
				continue	
			
			if startname in nodeMap:
				startid = nodeMap[startname]			
			else:
				results.append(str(nodes[0])+"\t"+nodes[1]+"\t"+"NA"+"\t"+"NA"+"\t"+"no matched compound")
				continue
			
			if endid>0 and startid>0:
				result=predictSLAP(weightMap,startid,endid)
				if result[2]==2:
					results.append(str(nodes[0])+"\t"+nodes[1]+"\t"+str(result[0])+"\t"+str(result[1])+"\t"+"binding")
				elif result[2]==1:
					results.append(str(nodes[0])+"\t"+nodes[1]+"\t"+str(result[0])+"\t"+str(result[1])+"\t"+"expression")
				else:
					results.append(str(nodes[0])+"\t"+nodes[1]+"\t"+str(result[0])+"\t"+str(result[1])+"\t"+"predicted")

	infile.close()
	return results

def predictSLAP(weightMap,startid,endid):

	path2 = "/var/www/html/rest/Chem2Bio2RDF/slap/"
	#path2=""
	maxL = 3
	op = 2
	result =  pathfinder_rank5.retrieveScore(weightMap,startid, endid, op, maxL, path2)
	return result


#submit jobs, return the file name where the result file is
def submitJobs(inputFile):
	baseFile="/var/lib/tomcat/webapps/slap/temp/"

	# tuple of all parallel python servers to connect with
	ppservers = ()

	if len(sys.argv) > 1:
		ncpus = int(sys.argv[1])
		# Creates jobserver with ncpus workers
		job_server = pp.Server(ncpus, ppservers=ppservers)
	else:
		# Creates jobserver with automatically detected number of workers
		job_server = pp.Server(ppservers=ppservers)

	#print "Starting pp with", job_server.get_ncpus(), "workers"

	infile = open(baseFile+inputFile, "r")
	#check the number of pairs
	pairs=infile.readlines()
	pairs_count=len(pairs)
	
	#check the input format is the default (i.e., cid, gene symbol)
	pair=pairs[1].split("\t")
	needPreprocess=1
	#if pair[0].isdigit and odbc6.isGene(pair[1]):
		#needPreprocess=0

	#only 500 pairs are allowed
	if pairs_count>500:
		pairs_count=500

	interval=int(math.ceil(pairs_count/5.00))
	inputs=[]
	#group the pairs into 5
	for i in (1,2,3,4,5):
		maxLine=i*interval
		inputs.append(maxLine)

	jobs = []
	for input in inputs:
		jobs.append(job_server.submit(predict,(inputFile,interval,input,needPreprocess), (predictSLAP,getNodeID,), ("pathfinder_rank5","odbc6",)))

	outputData=''
	outPut = open(baseFile+inputFile+".slap","w")

	job_server.wait()

	for job in jobs:
		results= job()
		for line in results:
			if line:
				outputData=outputData+line+"\n"
	outPut.write(outputData)
	outPut.closed

	return str(inputFile)

#submitJobs("test.txt")

