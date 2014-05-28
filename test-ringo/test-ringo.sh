#!/bin/bash
#
# Test script for Ringo python programs
#
# The test commands and descriptions are read from test-snapr.txt
# Please refer to test-snapr.txt for details of the benchmarks
#

grep -e '^$\|^\s*#' -v test-ringo.txt | sed 's/^\"//;s/\"$//' | while read line1; do
    read line2
    echo "***" `date` "$line1 ..."
    $line2
    RETVAL=$?
    if [ $RETVAL -ne 0 ]; then
        echo "***" `date` "ERROR: $line1"
        exit $RETVAL
    fi;
done
