## ﻿SLAP Dependencies

SLAP is a complex application comprised of many components, which are dependent on several external components and toolkits, listed here.  In cases where the dependence is indirect (esp. Chem2Bio2RDF) this is indicated.  It should be noted that runtime dependencies and preprocessing dependencies exist.  Building Chem2Bio2RDF and the path files are pre-requisites for SLAP to run.

|Dependency|SLAP component|Comment|
|---|---|---|
|Java|web app||
|Tomcat|web app||
|CytoscapeWeb|web app|Flash plugin for graph visualization|
|Java Molecular Editor (JME)|web app|Java applet|
|JQuery|web app||
|CDK|web app
|BioJava|web app
|BLAST|web app|(optional feature)
|Apache HTTPD|REST API
|Python|REST API
|mod_python|REST API|Apache module
|pp|REST API|Python package
|psycopg2|REST API|Python package
|SOAPpy|REST API|Python package
|SPARQLWrapper|REST API|Python package
|R (until spring 2014)|REST API|(Formerly called via Python; replaced in 2014 to resolve incident.)|
|NCBI Entrez eUtils||Runtime external webservice calls.|
|C++|preprocessing|Some source code missing.  Replacement (Python) under development.|
|Virtuoso?|preprocessing|Some preprocessing steps not fully documented.|
|PostgreSQL|Chem2Bio2RDF|(SLAP depends on subset of C2B2R.)|
|gNova Chord|Chem2Bio2RDF|chemical cartridge for PG (being replaced by OpenChord in cloud/dev version)|
|OpenEye OEChem|Chem2Bio2RDF|commercial or academic cheminfo toolkit (being replaced by OpenBabel in cloud/dev version).|
|Source DBs, e.g. PubChem, ChEMBL, many others.|Chem2Bio2RDF||

## SLAP Source code inventory

These counts are precise but may not accurately reflect code quantity.  Many apparently redundant files not counted.  Pre-processing done “by hand” not reflected.  

|Code|SLAP component|Line Count|
|---|---|---|
|Java|web app|2726|
|JSP|web app|3320|
|Python|REST API|6894|
|SQL|REST API|(Contained in Python, not counted separately.)|
|C++|preprocessing|?|
|Python|preprocessing|281 (new findpath.py)|
