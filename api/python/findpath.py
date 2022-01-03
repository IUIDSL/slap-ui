#!/usr/bin/env python
''' Should function as binary executable "findPath_m".

Given the input start and end IDs, must find shortest paths up to
length MAX_PATH.  Output format starts with delimiter line
"find ans", then lines for each node and edge, in path order,
each line format "ID URI".
The compiled program reportedly uses the Dijkstra algorithm.
Perhaps we can use Python package python-graph, which offers the
same algorithm (https://code.google.com/p/python-graph/).

author:	Jeremy Yang
'''
import sys,os,getopt,re,time,codecs,random

import pygraph.classes.graph # graph
import pygraph.algorithms.searching #breadth_first_search,depth_first_search
import pygraph.algorithms.minmax #shortest_path
#import pygraph.readwrite.dot #write

OP=2
MAX_PATH=4

#############################################################################
def GetNodeAttr(gr,node,attr):
  attrs = {k:v for k,v in gr.node_attributes(node)}
  return attrs[attr] if attrs.has_key(attr) else None

#############################################################################
def ReadGraph(nodefile,graphfile):

  gr = pygraph.classes.graph.graph()

  fin=open(nodefile)
  if not fin: ErrorExit('ERROR: cannot open nodefile: %s'%nodefile)
  while True:
    line=fin.readline()
    if not line: break
    fields = line.rstrip().split()
    if len(fields)==2:
      nid,nuri = fields
      nid = int(nid)
      gr.add_node(nid)
      gr.add_node_attribute(nid,('uri',nuri))
  fin.close()

  fin=open(graphfile)
  if not fin: ErrorExit('ERROR: cannot open graphfile: %s'%graphfile)
  i_line=0; n_link=0;
  lineA=None; lineB=None;
  while True:
    line=fin.readline()
    if not line: break
    i_line+=1
    if i_line==1:
      n = int(line)
      print >>sys.stderr, '%s: expecting nodes numbered 0 to: %d'%(PROG,n-1)
      continue
    if not lineA:
      lineA=line.rstrip()
    elif not lineB:
      lineB=line.rstrip()
    elif lineA and lineB and not line.strip():
      #print >>sys.stderr, 'DEBUG: lineA = "%s"'%lineA
      try:
        nodeID, j = lineA.split()
        nodeID = int(nodeID)
        j = int(j)
        fields = map(lambda x:int(x),lineB.split())
      except Exception,e:
        print >>sys.stderr, 'ERROR: '+str(e)
        lineA=None; lineB=None; continue #reset

      if len(fields)%2:
        print >>sys.stderr, 'ERROR: dangling link.'
        sys.exit()
      if len(fields) != 2*j:
        print >>sys.stderr, 'ERROR: format error, fieldcount != %d'%j
        sys.exit()
      edges_this = [fields[2*i] for i in range(len(fields)/2)]
      nodes_this = [fields[2*i+1] for i in range(len(fields)/2)]
      for i in range(len(edges_this)):
        edgeID=edges_this[i]
        if not gr.has_edge( (nodeID,nodes_this[i]) ):
          #Label edgeID mapped to URI via edges dict.
          gr.add_edge( (nodeID,nodes_this[i]), wt=1, label=edgeID )
          n_link+=1
      lineA=None; lineB=None; #reset

  fin.close()
  return gr

#############################################################################
def FindPaths(gr,edges,start,end):
  spst,dist = pygraph.algorithms.minmax.shortest_path(gr,startid)
  if dist.has_key(endid):
    end_attrs = {k:v for k,v in  gr.node_attributes(endid)}
    #print >>sys.stderr, "DEBUG: end_attrs = %s"%str(end_attrs)
    print >>sys.stderr, "shortest path from %s to %s..."%(startid,endid)
    d=dist[endid]
    s=spst[endid]
    pathnodes = [s]
    for i in range(d-2):
      pathnodes.insert(0,spst[pathnodes[-1]])
    if d>1: pathnodes.insert(0,startid)
    pathnodes.append(endid)
    pathedges = []
    for i in range(1,d+1):
      pathedges.insert(0,gr.edge_label((pathnodes[-i-1],pathnodes[-i])))
    print >>sys.stderr, "\tdist(%4s,%4s) =  %d :"%(startid,endid,d)
    print >>sys.stderr, "\t%s"%(pathnodes[0]),
    for i in range(len(pathedges)):
      print >>sys.stderr, "-(%s)-> %s"%(pathedges[i],pathnodes[i+1]),
    print >>sys.stderr, ""
    print >>sys.stderr, "\t%s"%(GetNodeAttr(gr,pathnodes[0],'uri')),
    for i in range(len(pathedges)):
      print >>sys.stderr, "-(%s)-> %s"%(edges[pathedges[i]],GetNodeAttr(gr,pathnodes[i+1],'uri')),
    print >>sys.stderr, ""


#############################################################################
def MyReadGraph(nodefile,graphfile):

  nodes={};
  fin=open(nodefile)
  if not fin: ErrorExit('ERROR: cannot open nodefile: %s'%nodefile)
  while True:
    line=fin.readline()
    if not line: break
    fields = line.rstrip().split()
    if len(fields)==2:
      nid,nuri = fields
      nodes[nuri]=nid
  if verbose:
    print >>sys.stderr, '%s: nodes: %d'%(PROG,len(nodes))
  fin.close()

  ## Represent graph as a dict of dict of lists,
  ## links[nodeID][edgeID] = [list of linked nodeIDs]
  links={};
  fin=open(graphfile)
  if not fin: ErrorExit('ERROR: cannot open graphfile: %s'%graphfile)
  i_line=0; n_link=0;
  lineA=None; lineB=None;
  while True:
    line=fin.readline()
    if not line: break
    i_line+=1
    if i_line==1:
      n = int(line)
      print >>sys.stderr, '%s: expecting nodes numbered 0 to: %d'%(PROG,n-1)
      continue
    if not lineA:
      lineA=line.rstrip()
    elif not lineB:
      lineB=line.rstrip()
    elif lineA and lineB and not line.strip():
      #print >>sys.stderr, 'DEBUG: lineA = "%s"'%lineA
      try:
        nodeID, j = lineA.split()
        nodeID = int(nodeID)
        j = int(j)
        fields = map(lambda x:int(x),lineB.split())
      except Exception,e:
        print >>sys.stderr, 'ERROR: '+str(e)
        lineA=None; lineB=None; continue #reset

      if len(fields)%2:
        print >>sys.stderr, 'ERROR: dangling link.'
        sys.exit()
      if len(fields) != 2*j:
        print >>sys.stderr, 'ERROR: format error, fieldcount != %d'%j
        sys.exit()
      links[nodeID] = {}
      edges_this = [fields[2*i] for i in range(len(fields)/2)]
      nodes_this = [fields[2*i+1] for i in range(len(fields)/2)]
      for i in range(len(edges_this)):
        edgeID=edges_this[i]
        if links[nodeID].has_key(edgeID):
          links[nodeID][edgeID].append(nodes_this[i])
        else:
          links[nodeID][edgeID]=[nodes_this[i]]
        n_link+=1
      lineA=None; lineB=None; #reset
  fin.close()
  print >>sys.stderr, '%s: total graph links: %d'%(PROG,n_link)

##############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  usage='''\
%(PROG)s

required:
        --start STARTID ............. nodeID, start node (ID, not URI)
        --end ENDID ................. nodeID, end node (ID, not URI)
	--op OP ..................... [%(OP)d]
	--max_path N ................ max length (edges) [%(MAX_PATH)d]
	--nodefile NODEFILE ......... input file of nodes
	--edgefile EDGEFILE ......... input file of edges
	--graphfile GRAPHFILE ....... input file of graph links
parameters:
        --o OFILE ................... output file [stdout]
        --v ......................... verbose
        --h ......................... this help

'''%{   'PROG':PROG,
	'OP':OP,
	'MAX_PATH':MAX_PATH
        }

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  verbose=0;
  nodefile=None;
  edgefile=None;
  graphfile=None;
  startid=None;
  endid=None;
  ofile=None;
  opts,pargs=getopt.getopt(sys.argv[1:],'',['o=',
	'nodefile=',
	'edgefile=',
	'graphfile=',
	'start=','end=',
	'op=',
	'max_path=',
	'help','v'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--o': ofile=val
    elif opt=='--nodefile': nodefile=val
    elif opt=='--edgefile': edgefile=val
    elif opt=='--graphfile': graphfile=val
    elif opt=='--start': startid=int(val)
    elif opt=='--end': endid=int(val)
    elif opt=='--op': OP=int(val)
    elif opt=='--max_path': MAX_PATH=int(val)
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s\n%s'%(opt,usage))

  if ofile:
    fout=codecs.open(ofile,"w","utf8","replace")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=codecs.getwriter('utf8')(sys.stdout,errors="replace")

  if not (nodefile and edgefile and graphfile):
    ErrorExit('--nodefile, --edgefile and --graphfile required.\n%s'%(usage))

  t0=time.time()

  edges={};
  fin=open(edgefile)
  if not fin: ErrorExit('ERROR: cannot open edgefile: %s'%edgefile)
  while True:
    line=fin.readline()
    if not line: break
    fields = line.rstrip().split()
    if len(fields)==2:
      eid,euri = fields
      edges[int(eid)]=euri
  if verbose:
    print >>sys.stderr, '%s: edge types: %d'%(PROG,len(edges))
  fin.close()
  for eid,euri in edges.items():
    print >>sys.stderr, "%6d: %s"%(eid,euri)

  #MyReadGraph(nodefile,graphfile)

  #random.seed(1717)
  gr = ReadGraph(nodefile,graphfile)
  print >>sys.stderr, "nodes: %d, edges: %d"%(len(gr.nodes()),len(gr.edges()))

  FindPaths(gr,edges,startid,endid)


  print >>sys.stderr, ('%s: elapsed time: %s'%(PROG,time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))
