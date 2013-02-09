#!/bin/bash
if [ $# -lt 1 ]
then
    echo "usage: shorten.sh <inputdir>"
    exit 1
fi
FILES=$1/*
OUTPUTDIR=$1/short
mkdir $OUTPUTDIR
for f in $FILES
do
    fname=`basename $f`
    if [ "$fname" != "short" -a "$fname" != "shorten.sh" ]
    then
        sed -n '1,1000 p' $f > $OUTPUTDIR/short_$fname
    fi
done
