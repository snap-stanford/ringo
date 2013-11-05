"""
 Use case #1: create a coauthorship network and print its estimated diameter
"""

import sys
sys.path.append("..")
sys.path.append("../../ringo-engine-python")
import os
import time
import snap
import testutils

N_TEST_NODES = 10
ENABLE_TIMER = True
OUTPUT_TABLE_FILENAME = 'table.tsv'
OUTPUT_GRAPH_FILENAME = 'graph.tsv'

if len(sys.argv) < 2:
  print """Usage: python 01-DBLP-snap.py source [destination]
  source: input DBLP .tsv file
  destination: output directory (for saving the table of edges and the coauthorship network)"""
  exit(1)
srcfile = sys.argv[1]
dstfile = sys.argv[2] if len(sys.argv) >= 3 else None
try:
  os.makedirs(dstfile)
except OSError:
  pass

context = snap.TTableContext()

t = testutils.Timer(ENABLE_TIMER)

# Load data
# >>> authors = ringo.load('authors.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("Key", snap.atStr))
S.Add(snap.TStrTAttrPr("Author", snap.atStr))
T = snap.TTable.LoadSS("1", S, srcfile, context, '\t', snap.TBool(False))
t.show("load")

# Self-join
# >>> authors.selfjoin(authors, ['Key'])
T = T.SelfJoin("Key")
t.show("join")

# Save final table
# >>> rank.save('table.tsv')
if not dstfile is None:
  T.SaveSS(os.path.join(dstfile,OUTPUT_TABLE_FILENAME))
  t.show("save edge table")

# Create network
# >>> authors.graph('Author_1', 'Author_2', directed=False)
# TODO: use simpler conventions for column renaming
SrcCol = "1_1.Author"
DstCol = "1_2.Author"
T.SetSrcCol(SrcCol)
T.SetDstCol(DstCol)
G = T.ToGraph(snap.FIRST)
t.show("graph")

if not dstfile is None:
  G.Save(snap.TFOut(os.path.join(dstfile,OUTPUT_GRAPH_FILENAME)))
  t.show("save graph")

# Print diameter
# >>> print graph.diameter(10000)
diameter = snap.GetBfsEffDiam(G,N_TEST_NODES)
t.show("diameter (%d test nodes)" % N_TEST_NODES)

print "Diameter: {0:.5f}".format(diameter)
