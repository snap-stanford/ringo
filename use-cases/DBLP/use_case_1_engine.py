"""
 Use case #1: create a coauthorship network and print its estimated diameter
"""

import sys
sys.path.append('../../ringo-engine-python')
import time
import snap
import ringo2

NTestNodes = 10

if len(sys.argv) < 2:
  print """Usage: python use_case_1.py source
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
  T = ringo.SelfJoin(T, "Key")

with Timer('graph'):
  # TODO: use simpler conventions for column renaming
  G = ringo.ToGraph(T, '1_1.Author','1_2.Author')

with Timer('diameter (%d test nodes)' % NTestNodes):
  diameter = snap.GetBfsEffDiam(G,NTestNodes)

print "Diameter: {0:.5f}".format(diameter)
