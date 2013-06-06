#!/usr/bin/python
import sys,os
ROOT_DIR = os.path.join(os.path.dirname(__file__),"..")
sys.path.append(ROOT_DIR)
import ringo
import time

NUM_TRIALS = 10
TEST_DIR = os.path.join(ROOT_DIR,"test")
QUERY_DIR = os.path.join(TEST_DIR,"queries")
DATA_DIR = os.path.join(TEST_DIR,"data")

rg = ringo.Ringo()

print "Building Q&A graph..."
start = time.clock() # processor time on Unix, wall-clock time on Windows
for i in xrange(NUM_TRIALS):
  rg.add_table(os.path.join(DATA_DIR,"posts.tsv"))
  rg.make_graph(os.path.join(QUERY_DIR,"qa.rg"), None, True)
print "Average time for Q&A graph: " + str((time.clock() - start)/NUM_TRIALS) + " seconds"

print "Building Common Comments graph..."
start = time.clock()
for i in xrange(NUM_TRIALS):
  rg.add_table(os.path.join(DATA_DIR,"comments.tsv"))
  rg.make_graph(os.path.join(QUERY_DIR,"comments.rg"), None, True)
print "Average time for Common Comments graph: " + str((time.clock() - start)/NUM_TRIALS) + " seconds"
