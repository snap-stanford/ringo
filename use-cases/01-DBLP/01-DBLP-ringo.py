"""
 Use case #1: create a coauthorship network and print its estimated diameter
"""

import sys
sys.path.append("..")
sys.path.append("../../ringo-engine-python")
import time
import snap
import ringo
import testutils
import pdb

N_TEST_NODES = 10
ENABLE_TIMER = True

if len(sys.argv) < 2:
  print """Usage: python use_case_1.py source [destination]
  source: input DBLP .tsv file
  destination: file where the coauthorship network should be stored"""
  exit(1)
srcfile = sys.argv[1]
dstfile = sys.argv[2] if len(sys.argv) >= 3 else None

ringo = ringo.Ringo()

t = testutils.Timer(ENABLE_TIMER)
S = [("Key","string"), ("Author","string")]
T = ringo.LoadTableTSV(S, srcfile)
t.show("load")

T = ringo.SelfJoin(T, "Key")
t.show("join")

# TODO: use simpler conventions for column renaming
G = ringo.ToGraph(T, "1_1.Author","1_2.Author")
t.show("graph")

if not dstfile is None:
  G.Save(snap.TFOut(dstfile))
  t.show("save")

diameter = snap.GetBfsEffDiam(G,N_TEST_NODES)
t.show("diameter (%d test nodes)" % N_TEST_NODES)

print "Diameter: {0:.5f}".format(diameter)
