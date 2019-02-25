#!/bin/sh
#############################################################################
### Example: PPARG is node ID 2020.  CID 5591 is node ID 179.
#############################################################################
#
date
printf "host: %s\n" `hostname`
#
NODEFILE="data/dicts/node2id.txt"
EDGEFILE="data/dicts/edge2id.txt"
GRAPHFILE="data/dicts/graph.txt"
#
OFILE="data/out/findpath_out.txt"
#
OP="2"
MAX_PATH="3"
#
if [ $# -ne 2 ]; then
	printf "ERROR:\tSyntax: `basename $0` STARTID ENDID\n"
	exit
fi
#
#
STARTID=$1
ENDID=$2
#
set -x
#
./findpath.py \
        --v \
        --start $STARTID \
        --end $ENDID \
	--op $OP \
	--max_path $MAX_PATH \
	--nodefile $NODEFILE \
	--edgefile $EDGEFILE \
	--graphfile $GRAPHFILE \
        --o $OFILE
#
