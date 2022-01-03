# slap-api

Code from SLAP, mostly by Bin Chen prior to 2012, as developed and hosted on
cheminfov.informatics.indiana.edu,  with some new client code and
documentation.

---

The program findPath_m is a compiled executable which I am now trying to
reverse engineer.  From the Python we can see its syntax, e.g.

"findPath_m /var/www/html/rest/Chem2Bio2RDF/slap/Dicts/ 2 179 2020 3"

The args are called (op, startid, endid, maxL).  

The node IDs should have already been found from the names.  

For example:
	Compound CID 5591 is node ID 179.
	Gene PPARG is node ID 2020.

The output of the program looks like this:

```
success!0
10000
20000
30000
40000
50000
60000
70000
80000
90000
100000
110000
120000
130000
140000
150000
160000
170000
180000
190000
200000
210000
220000
230000
240000
250000
260000
270000
280000
290000
load finish
Find the shortest path from 179 to 2020within length3
bfs finish
find ans
179 http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5591
0 http://chem2bio2rdf.org/substructure
113 http://chem2bio2rdf.org/drugbank/resource/substructure/Hydroquinones
0 http://chem2bio2rdf.org/substructure
615 http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/853
2 http://chem2bio2rdf.org/chemogenomics/resource/expression
2020 http://chem2bio2rdf.org/uniprot/resource/gene/PPARG
find ans
179 http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5591
0 http://chem2bio2rdf.org/substructure
114 http://chem2bio2rdf.org/drugbank/resource/substructure/Methoxyphenols
0 http://chem2bio2rdf.org/substructure
615 http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/853
2 http://chem2bio2rdf.org/chemogenomics/resource/expression
2020 http://chem2bio2rdf.org/uniprot/resource/gene/PPARG
find ans
...
```

Given the number 290000, it seems likely that the program is reading
file node2id.txt, which has 295898 lines.

Using the Unix "strings" program, we can see that several filenames 
are hard coded: node2id.txt, edge2id.txt, graph.txt.

As we can see, the program finds paths from a startid to endid, up to a 
maximum length.  Each path is reported after a "find ans" line, and
consists of E edges and E+1 nodes, where E <= maxL.

I will try to write an equivalent program in Python.

