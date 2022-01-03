# ﻿SLAP troubleshooting

How to diagnose and correct problems when SLAP malfunctions.  That is, the web app http://cheminfov.informatics.indiana.edu:8080/slap.


* SLAP the web app depends on Tomcat, Apache-HTTPD, and Postgresql.  
Are these services running?  Restarting services may correct problem.
* Note that SLAP does not depend on Virtuoso [right?].
* The web app depends on the SLAP REST API, as documented at http://slapfordrugtargetprediction.wikispaces.com/API.  Test the REST API.  Example URLs:
   * http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/5591:PPARG
* If the SLAP REST API does work, perhaps the Tomcat web app itself is the problem.  Restart Tomcat.  If needed, the files are in /usr/share/tomcat5/webapps/slap/.  
* If the SLAP REST API does not work, try some other REST requests.  These use Apache-HTTPD (port 80).  If these fail the problem could be Apache-HTTPD.
   * http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/Bayes_Model/5880:NR1I2
   * http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/Sea_Model/5591:PPARG
* Note that REST API testing can be done via various clients (wget, curl, browsers).  It seems that error messages are sometimes client dependent, and browsers show mod_python errors which wget does not.
* The REST API depends on Python programs which can be run locally (http://slapfordrugtargetprediction.wikispaces.com/SLAP+interfaces).  Files are in /var/www/html/rest/Chem2Bio2RDF/slap/.
* Please do not make any irreversible changes!  Document any changes.


## Packages used by SLAP

|Package|Comment|
|---|---|
|Apache HTTPD|webserver|
|Apache Tomcat|Java servlet container|
|JME|Java Molecular Editor (applet)|
|JQuery|JavaScript library|
|CytoscapeWeb|Flash plugin for network visualization|
|CDK|Cheminfo Java kit used by webapp (maybe)|
|BioJava|Java kit used by webapp (maybe)|
|Blast|Used by webapp (maybe)|
|R|Used by webservice (previous to May 2014)|
|Virtuoso|(Not used by SLAP at runtime, I think.  However, dir exists at /var/www/html/rest/Chem2Bio2RDF/slap/virtuoso.|
|C++|(or maybe other compiled language) See compiled binary executables in /var/www/html/rest/Chem2Bio2RDF/slap: findPath_m, pathfinder_m (maybe not needed, see pathfinder_m.py), PreProcess (maybe not needed)|
|Psycopg2|Python API for Postgres|
