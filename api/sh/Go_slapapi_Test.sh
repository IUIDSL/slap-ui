#!/bin/sh
#
set -x
#
#wget -q -O - 'http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/_info'
#
rest_request.py 'http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/_info'
#
rest_request.py 'http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/cid_gene/5591:PPARG'
rest_request.py 'http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/cid_gene/Prozac:PPARG'
rest_request.py 'http://ec2-54-88-170-209.compute-1.amazonaws.com/rest/slap/cid_gene/NCCc1cc(O)c(O)cc1:PPARG'
