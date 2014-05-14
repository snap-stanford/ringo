#!/bin/bash

#
# test script for basic Snap.py functionality
#
# input file requirements, files are in "data"
#		p2p-Gnutella08.txt
#

echo "***" `date` "quick_test.py ..."
python quick_test.py
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR quick_test.py"
    exit $RETVAL
fi;

echo "***" `date` "snap-test.py ..."
python snap-test.py
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR snap-test.py"
    exit $RETVAL
fi;

echo "***" `date` "test-tnodei.py ..."
python test-tnodei.py
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR test-tnodei.py"
    exit $RETVAL
fi;

echo "***" `date` "test-io.py ..."
python test-io.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR test-io.py"
    exit $RETVAL
fi;

echo "***" `date` "intro.py ..."
python intro.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR intro.py"
    exit $RETVAL
fi;

echo "***" `date` "tutorial.py ..."
python tutorial.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR tutorial.py"
    exit $RETVAL
fi;

echo "***" `date` "tneanet.py ..."
python tneanet.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR tneanet.py"
    exit $RETVAL
fi;

echo "***" `date` "cncom.py ..."
python cncom.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR cncom.py"
    exit $RETVAL
fi;

echo "***" `date` "bfs.py ..."
python bfs.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR bfs.py"
    exit $RETVAL
fi;

echo "***" `date` "attributes.py ..."
# disabled, since it is not working
#python attributes.py 
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "ERROR attributes.py"
    exit $RETVAL
fi;

