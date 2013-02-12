#!/bin/bash
if [ $# -lt 1 ]
then
    echo "usage: shfile.sh <inputfile>"
    exit 1
fi
F=$1
fname=`basename $F`
sed -n '1,1000 p' $F > short_$fname
