#!/usr/bin/env python
#############################################################################
# Works via:
#   http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/_info
# with httpd.conf alias:
#   Alias /rest/slap/_info /var/www/html/rest/slap/info.py
# installed:
#   vernon:/var/www/html/rest/slap
#
# Jeremy Yang
# 31 Oct 2014
#############################################################################
import sys,os,re,time,json
import cgi

import slapdb_utils
import slapapi_utils

#############################################################################
def API_HelpTxt(prefix):
  return '''\
SLAP REST API:

\t%(PREFIX)s/_info
\t%(PREFIX)s/cid_gene?CID:GENESYMBOL
e.g.
\t%(PREFIX)s/cid_gene?5591:PPARG
'''%{'PREFIX':prefix}

#############################################################################
if __name__=='__main__':

  print "Content-type: text/plain\n\n"

  ### From httpd config.
  SLAPDB_HOST=os.environ['SLAPDB_HOST']
  SLAPDB_NAME=os.environ['SLAPDB_NAME']
  SLAPDB_SCHEMA=os.environ['SLAPDB_SCHEMA']
  SLAPDB_USER=os.environ['SLAPDB_USER']
  SLAPDB_PW=os.environ['SLAPDB_PW']

  FORM=cgi.FieldStorage(keep_blank_values=1)

  debug = True if FORM.getvalue('debug') else False
  expand = True if FORM.getvalue('expand') else False

  dbcon = None
  try:
    dbcon = slapdb_utils.Connect(dbhost=SLAPDB_HOST,dbname=SLAPDB_NAME,dbusr=SLAPDB_USER,dbpw=SLAPDB_PW)
  except Exception,e:
    slapapi_utils.HTTPErrorExit(500,'Database access error: %s'%str(e))

  api_prefix = os.path.dirname(os.environ['REQUEST_URI']) if os.environ.has_key('REQUEST_URI') else ''

  print API_HelpTxt(api_prefix)

  if debug:

    #cgi.print_environ()
    for envar in (
	'CONTEXT_DOCUMENT_ROOT',	#DEBUG
	'CONTEXT_PREFIX',	#DEBUG
	'PATH_INFO',	#DEBUG
	'PYTHONPATH',	#DEBUG
	'QUERY_STRING',	#DEBUG
	'REQUEST_URI',	#DEBUG
	'SCRIPT_NAME',	#DEBUG
	'SCRIPT_FILENAME',	#DEBUG
	'SERVER_NAME',	#DEBUG
	'SLAPDB_HOST',
	'SLAPDB_NAME'
	):
      print "DEBUG:\t%22s = %s"%('$'+envar,(os.environ[envar] if os.environ.has_key(envar) else ''))

    row = slapdb_utils.Info(dbcon,SLAPDB_SCHEMA)
    print json.dumps(row,indent=2)

    for key in FORM.keys():
      print 'DEBUG: FORM[%s] = "%s"'%(key,FORM[key].value)
