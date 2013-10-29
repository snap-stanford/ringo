"""
 Use case #1: create a coauthorship network and print its estimated diameter
"""

import sys
import snap
import time

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

with Timer('load'):
  srcfile = sys.argv[1]
  schema = snap.Schema()
  schema.Add(snap.TStrTAttrPr("Key",snap.atStr))
  schema.Add(snap.TStrTAttrPr("Author",snap.atStr))
  context = snap.TTableContext()
  T = snap.TTable.LoadSS("1",schema,srcfile,context)

with Timer('join'):
  T2 = T.SelfJoin("Key")

with Timer('graph'):
  T2.SetSrcCol('1_1.Author')
  T2.SetDstCol('1_2.Author')
  G = T2.ToGraph(snap.FIRST)

with Timer('diameter (%d test nodes)' % NTestNodes):
  diameter = snap.GetBfsEffDiam(G,NTestNodes)

print "Diameter: {0:.5f}".format(diameter)
