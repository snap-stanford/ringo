"""
 Use case #2: create a coauthorship network and get the table of authors sorted by PageRank score
"""

import sys
sys.path.append('../../ringo-engine-python')
import snap
import ringo2
import time

NTopAuthors = 20

if len(sys.argv) < 2:
  print """Usage: python use_case_2_engine.py source
  source: input DBLP .tsv file"""
  exit(1)

class Timer(object):
  def __init__(self,name):
    self.name = name
  def __enter__(self):
    self.start = time.time()
  def __exit__(self, type, value, traceback):
    print '[%s]\tElapsed: %.2f seconds' % (self.name, time.time() - self.start)

ringo = ringo2.ringo()

with Timer('load'):
  srcfile = sys.argv[1]
  S = {"Key":"string", "Author":"string"}
  T = ringo.LoadTableTSV(S, srcfile)

with Timer('join'):
  T2 = ringo.SelfJoin(T, "Key")

with Timer('select'):
  ringo.Select(T2, '1_1.Author != 1_2.Author')

with Timer('graph'):
  G = ringo.ToGraph(T2, '1_1.Author', '1_2.Author')

with Timer('page rank'):
  P = ringo.PageRank(G)

with Timer('order'):
  ringo.Order(P, ['PageRank'])

# Print top authors with their PageRank score
T3 = ringo.Tables[P]
RI = T3.BegRI()
print "{0: <30}PageRank".format("Name")
print "-----------------------------------------"
cnt = 0
while RI < T3.EndRI() and cnt < NTopAuthors:
  print "{0: <30}{1:.5f}".format(RI.GetStrAttr(ringo.NODE_ATTR_NAME), RI.GetFltAttr('PageRank'))
  RI.Next()
  cnt += 1