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

def predict(cid,maxLineNumber):
	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
	weightMap = pathfinder_rank5.getWeightMap("/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/pair_weight.txt", idx = (0,1), sep = "\t", skip = 1)
	nodeMap = getNodeID(file1,sep = " ")

	startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(cid)
	startname = nodeMap[startname]

	infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/validTargets.txt", "r")
	lineNumber=0
	results=[]
	for line in infile:
		line = line.strip()
		lineNumber +=1
		if (lineNumber>maxLineNumber-100 and lineNumber<=maxLineNumber) :
			endname = "http://chem2bio2rdf.org/uniprot/resource/gene/" + line
			endname = nodeMap[endname]

			result=predictSLAP(weightMap,startname,endname)
			results.append(str(cid)+"\t"+line+"\t"+str(result[0])+"\t"+str(result[1])+"\t"+str(result[2]))
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
def submitJobs(cid):

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

	#start_time = time.time()
	
	# The following submits 8 jobs and then retrieves the results
	inputs = (100,200,300,400,500,600,700)
	jobs = []
	for input in inputs:
		jobs.append(job_server.submit(predict,(cid,input), (predictSLAP,getNodeID,), ("pathfinder_rank5",)))

	outputData=''
	randomFile=str(random.random())
	outPut = open("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+"drug"+"."+str(cid), 'a')

	job_server.wait()

	for job in jobs:
		results= job()
		for line in results:
			outputData=outputData+line+"\n"
	outPut.write(outputData)
	outPut.closed

	#print "Time elapsed: ", time.time() - start_time, "s"
	#job_server.print_stats()
	return "drug"+"."+str(cid)   #+"."+randomFile
	#return outputData

def targetPrediction(cid):
	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
	nodeMap = getNodeID(file1,sep = " ")
	startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(cid)
	if startname not in nodeMap:
		smiles=odbc6.getSMILESByCID(cid)
		results=odbc6.getNeighbors(smiles)[0] #nearest neighbor
		cid=results.split("\t")[0]

	if os.path.exists("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+"drug"+"."+str(cid)):
		resultFile="drug"+"."+str(cid)
	else:
		resultFile=submitJobs(cid)

	os.popen("Rscript /var/www/html/rest/Chem2Bio2RDF/slap/stats.R "+resultFile)

	return resultFile

def targetPredictionForSim(cid1,cid2):
	file1 = "/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/target2id.txt"
	nodeMap = getNodeID(file1,sep = " ")

	startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(cid1)
	if startname not in nodeMap:
		smiles=odbc6.getSMILESByCID(cid1)
		results=odbc6.getNeighbors(smiles)[0] #nearest neighbor
		cid1=results.split("\t")[0]

	startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/" +str(cid2)
	if startname not in nodeMap:
		smiles=odbc6.getSMILESByCID(cid2)
		results=odbc6.getNeighbors(smiles)[0] #nearest neighbor
		cid2=results.split("\t")[0]

	#check whether in referred drug
	infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/referred_drugs.txt", "r")
	cid1_new=0
	cid2_new=0
	for line in infile:
		line=line.strip()
		if line == str(cid1):
			cid1_new=1
		if line == str(cid2):
			cid2_new=1

	#check whether exists
	if cid1_new==0:
		if os.path.exists("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+"drug"+"."+str(cid1)):
			cid1_new=1

	if cid2_new==0:
		if os.path.exists("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+"drug"+"."+str(cid2)):
			cid2_new=1

	if cid1_new==0:
		resultFile=submitJobs(cid1)

	if cid2_new==0:
		resultFile=submitJobs(cid2)

	os.popen("Rscript /var/www/html/rest/Chem2Bio2RDF/slap/drug_sim.R "+str(cid1)+" " +str(cid2))

	return str(cid1)+"_"+str(cid2)

#targetPredictionForSim(23667301,2153)

