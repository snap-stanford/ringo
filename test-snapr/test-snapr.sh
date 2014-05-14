#!/bin/bash

#
# test script for Ringo python programs
#
# the script verifies that all benchmarks complete successfully
# on a small subset of LiveJournal and StackOverflow
#
# input file requirements, files are in "data"
#	soc-LiveJournal1_small.txt
#	soc-LiveJournal1_50.txt
#	soc-LiveJournal1_450.txt
#	posts_scores_10k.tsv
#	posts_tags_10k.tsv
#	tags_10k.tsv
#

echo "***" `date` "01 read text table, save binary table ..."
#
# read input text file with 2 columns and build a table with 2 integer columns
# save table to file in the binary format
#
python 01-tbtxt2bin.py data/soc-LiveJournal1_small.txt soc-LiveJournal1.table
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "01 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "02 read binary table, create graph, convert to table ..."
#
# read table from a file with the binary format
# create a graph from the table
# create table from the graph
#
python 02-tbbin2gr2tb.py soc-LiveJournal1.table
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "02 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "03 read binary table, select new small table ..."
#
# read table from a file with the binary format
# select rows with the first value < 10000, create new table
#
python 03-tbselltnewtb.py soc-LiveJournal1.table
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "03 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "04 read binary table, select new large table ..."
#
# read table from a file with the binary format
# select rows with the first value > 10000, create new table
#
python 04-tbselgtnewtb.py soc-LiveJournal1.table
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "04 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "05 read binary table, select in-place small table ..."
#
# read table from a file with the binary format
# select rows with the first value < 10000, in place
#
python 05-tbselltinplace.py soc-LiveJournal1.table
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "05 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "06 read binary table, select in-place large table ..."
#
# read table from a file with the binary format
# select rows with the first value > 10000, in place
#
python 06-tbselgtinplace.py soc-LiveJournal1.table
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "06 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "07-1 read binary table and text table, small join ..."
#
# read two column table t1 from a file with the binary format
# read one column table t2 from a file with the text format format
# join t2 and t1 on first columns
#
python 07-join.py soc-LiveJournal1.table data/soc-LiveJournal1_50.txt
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "07-1 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "07-2 read binary table and text table, large join ..."
#
# read two column table t1 from a file with the binary format
# read one column table t2 from a file with the text format format
# join t2 and t1 on first columns
#
python 07-join.py soc-LiveJournal1.table data/soc-LiveJournal1_450.txt
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "07-2 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "08 read text StackOverflow table, sum user scores ..."
#
# reads the posts table from the Stackoverflow dataset, and for
# each user, computes the sum of the scores of this user's posts
#
python 08-groupaggr.py data/posts_scores_10k.tsv
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "08 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "09 read text StackOverflow table, find next user posts ..."
#
# reads the posts table form the StackOverflow dataset, and
# for each post finds the next post by the same user in chronological order
#
python 09-isnextk.py data/posts_scores_10k.tsv
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "09 ERROR"
    exit $RETVAL
fi;

# NOTE, this comment might be incorrect in the documentation
echo "***" `date` "10 read text StackOverflow table, find next user posts ..."
#
# reads the posts table form the StackOverflow dataset, and
# for each post, finds the next post by the same user in chronological order
#
python 10-graphseq.py data/posts_scores_10k.tsv
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "10 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "11 read text StackOverflow table, create graph of accepted answers ..."
#
# reads the post table from the StackOverflow dataset, and creates
# a graph for each topic, where in each graph, a user A points to a
# user B if A accepted at least one answer from B
#
python 11-graphgroup.py data/posts_scores_10k.tsv data/tags_10k.tsv
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "11 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "12 read text StackOverflow table, compute Python experts 1 ..."
#
# reads the post table from the StackOverflow dataset, creates a
# graph where user A points to user B if A accepted at least one
# answer from B for a question about Python, computes the PageRank
# score of each user in this graph, and saves the scores to a file
#
python 12-usecase.py data/posts_tags_10k.tsv out.bin
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "12 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "14 read text StackOverflow table, compute Python experts 2 ..."
#
# same as 12-usecase.py, except that a table of "questions"
# and a table of "answers" are explicitly created before joining
#
python 14-usecase-complete.py data/posts_tags_10k.tsv out.bin
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "14 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "50 read text table, create PNGraph, save binary graph ..."
#
# read input text file with two columns and build a PNGraph
# save PNGraph to file in the binary format
#
python 50-grtxt2bin.py data/soc-LiveJournal1_small.txt soc-LiveJournal1.graph
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "50 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "51 read binary PNGraph, compute pagerank ..."
#
# read PNGraph from a file with the binary format
# calculate pagerank
#
python 51-grpagerank.py soc-LiveJournal1.graph
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "51 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "52 read text table, create PNEANet, save binary graph ..."
#
# read input text file with two columns and build a PNEANet
# save PNEANet to file in the binary format
#
python 52-nettxt2bin.py data/soc-LiveJournal1_small.txt soc-LiveJournal1.net
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "52 ERROR"
    exit $RETVAL
fi;

echo "***" `date` "53 read binary PNEANet, compute pagerank ..."
#
# read PNEANet from a file with the binary format
# calculate pagerank
#
python 53-netpagerank.py soc-LiveJournal1.net
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "***" `date` "53 ERROR"
    exit $RETVAL
fi;

