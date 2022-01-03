#!/usr/bin/env python

###
from mod_python import apache
###
# NOTE: mod_python only required for apache.OK, which is constant 0.  Trying to drop mod_python.
###

import string
import sys
import SOAPpy
import odbc6
import ppDrugTargetPrediction1
import ppPairPrediction2

import pathfinder_rank5
import commands
import random
import time

from xml.dom.minidom import parse 
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
import os
#os.environ['PYTHON_EGG_CACHE'] = '/var/www/html/rest/Chem2Bio2RDF/.python-eggs'


def handler(req):
	#uriParts="http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/5880:NR1I2"
	#uriParts="http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/cid=5880"
	#uriParts="http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/gene=pxr"

	#uriParts="http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/CHEBI_155189:68617&5203&13408686&9882979:NR1I2"
	#uriParts="http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/upload_test.txt"

	#write all the request
	infile=open("/var/www/html/rest/Chem2Bio2RDF/slap/temp/requests.txt",'a')
	infile.write(req.uri+"\t"+req.get_remote_host()+"\t"+time.strftime('%X %x %Z')+"\n")
	infile.close()


	path2 = "/var/www/html/rest/Chem2Bio2RDF/slap/"
	maxL = 3
	op = 2
	result=[]

	output = commands.getoutput('ps -A | grep findPath_m').split("\n")
	if len(output)>10:
   		req.write("please try again later, all the threads are being used")
		return apache.OK 
		#return 0
	
	#if request from upload 
	if req.uri.find("upload_")>0:
		url=req.uri
		fileName=url[(url.find("upload_")+7):len(url)]
		results=ppPairPrediction2.submitJobs(fileName)
    		req.content_type = 'text/html'
    		req.write("<html>\n\n")
    		req.write("<head>\n")
    		req.write("<title>SLAP results</title>\n")
    		req.write("</head>\n\n")
    		req.write("<body>\n\n")
		req.write("<a href=\"http://cheminfov.informatics.indiana.edu:8080/slap/temp/"+fileName+".slap\">download the results</a>")
		req.write("</body>\n\n")
		req.write("</html>\n\n")

		return apache.OK 
		#return 0

	#if request for drug similarity
	if req.uri.find("sim_")>0:
		uriParts = req.uri.split(':')
		if(len(uriParts) == 2):
			cid2 = uriParts[-1]
			url=uriParts[0]
			cid1=url[(url.find("sim_")+4):len(url)]
			cid1=str(odbc6.checkCompound(str(cid1)))
			cid2=str(odbc6.checkCompound(str(cid2)))
			result=ppDrugTargetPrediction1.targetPredictionForSim(str(cid1),str(cid2))

			try:
				infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+str(cid1)+"_"+str(cid2), "r")
			except IOError :
				req.write("failed")
				return apache.OK
				#return 0

			for line in infile:
				req.write (line)
			
		return apache.OK
		#return 0


	uriParts = req.uri.split(':')
       #uriParts = uriParts.split(':')
	if(len(uriParts) == 2):
		temp = uriParts[-1]

		if temp.find("&")== -1: #input is cid:gene
			cid = (uriParts[-2].split('/')[-1])
			cid=str(odbc6.checkCompound(str(cid)))
			
			gene=odbc6.checkTarget(temp)
			if len(cid)>0 and len(gene)>0:
				startname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(cid)
				endname = "http://chem2bio2rdf.org/uniprot/resource/gene/"+gene
				results =  pathfinder_rank5.generalSearch(startname, endname, op, maxL, path2)
				if str(results[0])=="0" :
					req.write("target was not found")
				elif str(results[0])=="1" :
					req.write("compound was not found")
				elif str(results[0])=="2" :
					req.write("no valid path was found")
				else :
					if str(results[3]).strip() == '2':
						type="<a href=\"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+str(cid)+":"+gene+"\">"+"approved binding"+"</a>"
					elif str(results[3]).strip() == '1':
						type="<a href=\"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+str(cid)+":"+gene+"\">"+"approved expression"+"</a>"
					else:
						type="predicted"
					req.write("<b><i>Input: </i></b> Compound: "+str(cid)+"; Target: "+gene+"\n")
					req.write("<b><i>P value: </i></b>"+str(results[1])+" ("+str(results[0])+")"+"\n"+"<b><i>Type: </i></b>"+type)
					req.write("\n*Smaller p value, stronger association\n")
					req.write(results[4])
					

			else:
				if len(cid)==0:
					req.write("compound was not found")
				else:
					req.write("target was not found")

			return apache.OK        
			#return 0

			
		else:	#input is compound input: cids
			cids=temp.split('&')		
			if cids.count('')>0:		
				cids.remove('')  #remove invalid cid

			input_cid=str(uriParts[-2].split('/')[-1])
			results=odbc.cidNetworks(input_cid,cids)
			req.write(results)
			return apache.OK
			#return 0
	
	#two : are not allowed
	elif (len(uriParts) > 3) :
		req.write("only one ':' is allowed in the url")
		return apache.OK
		#return 0

		gene = uriParts[-1]
		strcids = uriParts[-2]
		input = (uriParts[-3].split('/')[-1])
		originalname = "http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+str(input)
		startnames=[]
		cids=strcids.split('&')

		for cid in cids:
			startnames.append("http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+cid)
	
		endname = "http://chem2bio2rdf.org/uniprot/resource/gene/"+gene
		results =  pathfinder_rank5.generalSearchBatchCIDs(originalname ,startnames, endname, op, maxL, path2)
	elif (len(uriParts) == 1):
		input = str(uriParts[-1].split('/')[-1])	
		if input.find("cid")>-1:
			cid=str(input.split("cid=")[-1])
			input=str(odbc6.checkCompound(cid))
			if input.isdigit() and len(input)>0:
				#print input
				#results="NA"+"\n"+"NA"+"\n"+odbc.cidNetwork(input)
				result=ppDrugTargetPrediction1.targetPrediction(input)
				#result="1986.0.266584606072"

    				req.content_type = 'text/html'
    				req.write("<html>\n\n")
    				req.write("<head>\n")
    				req.write("<title>SLAP results</title>\n")
    				req.write("</head>\n\n")
    				req.write("<body>\n\n")
				req.write("<p><font size=\"5\">Your input is: "+str(cid)+" </p>")

				req.write("<p><font size=\"5\">Predicted Targets</p>")

				req.write("<table border=\"1\">")
				req.write("<tr>")
				req.write("<td>target</td><td>p value</td><td>score</td><td>type</td><td>chemohub</td>")
				req.write("<tr>")
				
				try:
					infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+result+".rank", "r")
				except IOError :
					req.write("No target predicted")
					return apache.OK
					#return 0

				for line in infile:
					items=line.split("\t")
					req.write("<tr>")
					req.write("<td><a href=\"http://chem2bio2rdf.org/uniprot/resource/gene/"+items[1]+"\">"+items[1]+"</a></td>")
					req.write("<td>"+items[3]+"</td>")
					req.write("<td>"+items[2]+"</td>")
					if items[4].strip() == '2':
						req.write("<td><a href=\"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/"+items[0]+":"+items[1]+"\">"+"approved interaction"+"</a></td>")
					elif items[4].strip() == "1":
						req.write("<td>approved expression</td>")
					else:
						req.write("<td>"+"predicted"+"</td>")
				
					req.write("<td><a href=\"http://cheminfov.informatics.indiana.edu:8080/slap/slap.jsp?cid="+items[0]+"&gene="+items[1]+"\">"+"see paths"+"</a></td>")
					
					req.write("</tr>")
				req.write("</table>")
				req.write("<p>* the smaller p value, the stronger association</p>")

				req.write("<p></p><p><font size=\"5\">Biological Similar Drugs</p>")

				req.write("<table border=\"1\">")
				req.write("<tr>")
				req.write("<td>PubChem CID</td><td>structure</td><td>Drug Name</td><td>Similarity</td><td>Related Diseases</td><td>ATC</td>")
				req.write("<tr>")
				
				try:
					infile = open("/var/www/html/rest/Chem2Bio2RDF/slap/temp/"+result+".similarDrugs", "r")
				except IOError :
					req.write("No similar drug found")
					return apache.OK
					#return 0
					
				for line in infile:
					items=line.split("\t")
					req.write("<tr>")
					req.write("<td><a href=\"http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+items[0]+"\">"+items[0]+"</a></td>")
					req.write("<td><img src=\"http://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?t=l&cid="+items[0]+"\" width=\"60\" height=\"60\" />" +"</td>")
					req.write("<td><a href=\"http://chem2bio2rdf.org/drugbank/resource/drugbank_drug/"+items[3]+"\">"+items[1]+"</a></td>")
				
					req.write("<td>"+items[2]+"</td>")
				
					diseases=items[4].split(";")
					req.write("<td>")
					for disease in diseases:
							omimID=odbc6.getOMIMID(disease)
							if omimID!='':
								req.write("<a href=\"http://chem2bio2rdf.org/omim/resource/omim_disease/"+str(omimID)+"\">"+disease.replace("_"," ")+"</a>"+"<br />")
							else:
								req.write(disease.replace("_"," ")+"<br />")
					req.write("</td>")

					atcs=items[5].split(";")
					req.write("<td>")
					for atc in atcs:
						req.write("<a href=\"http://www.whocc.no/atc_ddd_index/?code="+atc+"\">"+atc+"</a>"+"<br />")
					req.write("</td>")

				req.write("<a href=\"http://chem2bio2rdf.org/slap/temp/"+result+".signatures.txt"+"\">"+"download biological signatures"+"</a>"+"<br />")
				
			
		else :
			gene=str(input.split("=")[-1])
			input=str(odbc6.checkTarget(gene))
			if len(input)>0:
				results=odbc6.fetchTargetLigands(input)

				if len(results)<1:
					req.write("no ligands were found! You may want to use sequence search to find the most similar target in our database or ask us to have a look at your target")
					return apache.OK
					#return 0

    				req.content_type = 'text/html'
    				req.write("<html>\n\n")
    				req.write("<head>\n")
    				req.write("<title>SLAP results</title>\n")
    				req.write("</head>\n\n")
    				req.write("<body>\n\n")
				req.write("<p><font size=\"5\">Your input is: "+str(gene)+" </p>")

				req.write("<p><font size=\"5\">known ligands</p>")

				req.write("<table border=\"1\">")
				req.write("<tr>")
				req.write("<td>cid</td><td>structure</td><td>sources</td><td>slap</td><td>smiles</td>")
				req.write("</tr>")	
				for result in results:
					items=result.split("\t")
					req.write("<tr>")
					req.write("<td><a href=\"http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/"+items[0]+"\">"+items[0]+"</a></td>")
					req.write("<td><img src=\"http://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?t=l&cid="+items[0]+"\" width=\"150\" height=\"150\" />" +"</td>")
					req.write("<td>"+items[1]+"</td>")
					req.write("<td><a href=\"http://cheminfov.informatics.indiana.edu:8080/slap/slap.jsp?cid="+items[0]+"&gene="+input+"\">"+"see paths"+"</a></td>")
					req.write("<td>"+items[2]+"</td>")				

					req.write("</tr>")

				req.write("</table>")
				
				#list related targets			
				relatedTargets=''
				relatedTargets=odbc6.fetchTargetRelatedTargets(input)
				if len(relatedTargets)<1:
					req.write("no related targets were found, contact us for virtual screening.")
					return apache.OK
					#return 0

				relatedTargets=([v for v, k in relatedTargets])
				req.write("<p><font size=\"5\">Similar Targets by Ligand information</font></p>")

				for target in relatedTargets:
					req.write("<a href=\"http://chem2bio2rdf.org/uniprot/resource/gene/"+target +"\">"+target +"</a>  ")

				#prepare ligands for virtual screening
				baseFile="/var/lib/tomcat/webapps/slap/temp/"
				randomFile=str(input)+str(random.random())
				relatedCompounds=''
				relatedCompounds=odbc6.fetchTargetRelatedCompounds(input)

				if len(relatedCompounds)<1:
					req.write("no related compounds were found")
					return apache.OK
					#return 0

				outPut = open(baseFile+randomFile,"w")
				outputData=''
				for compound in relatedCompounds:
					outputData=outputData+compound+"\t"+str(input)+"\n"
				outPut.write(outputData)
				outPut.closed

				req.write("<br><br><a href=\"http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/upload_"+randomFile+"\">"+ "Virtual Screen compounds derived from related targets" +"</a>")
				req.write("<br>if you run virtual screening, it may take a couple of minutes. We only offer at most 500 compounds currently")
	
				req.write("</body>\n\n")
				req.write("</html>\n\n")
				
		return apache.OK
		#return 0

