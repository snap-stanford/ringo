"""
 Use case #1: create a coauthorship network and print its estimated diameter
"""

import sys
import snap
import time
import other_ringo as ringo

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


engine = ringo.ringo()
with Timer('load'):
  srcfile = sys.argv[1]
  A = engine.LoadTableTSV({'Key':'string', 'Author':'string'}, srcfile)

with Timer('join'):
  A2 = engine.Join(A, "Key")

with Timer('graph'):
  B = engine.Graph(A2, '1_1.Author', '1_2.Author')

with Timer('diameter (%d test nodes)' % NTestNodes):
  diameter = snap.GetBfsEffDiam(B,NTestNodes)

print "Diameter: {0:.5f}".format(diameter)
