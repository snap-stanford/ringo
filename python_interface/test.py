#!/usr/bin/python
import ringo
import time

NUM_TRIALS = 10
DATA_DIR = "data/"
rg = ringo.Ringo()

print "Building Q&A graph..."
start = time.clock() # processor time on Unix, wall-clock time on Windows
for i in xrange(NUM_TRIALS):
  rg.load_table(DATA_DIR + "posts.tsv")
  rg.make_graph(DATA_DIR + "qa.rg", None, True)
print "Average time for Q&A graph: " + str((time.clock() - start)/NUM_TRIALS) + " seconds"

print "Building Common Comments graph..."
start = time.clock()
for i in xrange(NUM_TRIALS):
  rg.load_table(DATA_DIR + "comments.tsv")
  rg.make_graph(DATA_DIR + "comments.rg", None, True)
print "Average time for Common Comments graph: " + str((time.clock() - start)/NUM_TRIALS) + " seconds"