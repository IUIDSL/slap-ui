#!/bin/sh
#############################################################################
### Example: PPARG is node ID 2020.  CID 5591 is node ID 179.
#############################################################################
#
date
printf "host: %s\n" `hostname`
#
FINDPATH_EXE="/var/www/html/rest/Chem2Bio2RDF/slap/findPath_m"
DATADIR="/var/www/html/rest/Chem2Bio2RDF/slap/Dicts/"
#
op="2"
maxL="3"
#
if [ $# -ne 2 ]; then
	printf "ERROR:\tSyntax: `basename $0` STARTID ENDID\n"
	exit
fi
#
#
startid=$1
endid=$2
#
set -x
#
cmd="$FINDPATH_EXE $DATADIR $op $startid $endid $maxL"
#
$cmd
