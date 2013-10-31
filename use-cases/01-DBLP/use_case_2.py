"""
 Use case #2: create a coauthorship network and get the table of authors sorted by PageRank score
"""

import sys
sys.path.append("..")
sys.path.append("../../ringo-engine-python")
import time
import snap
import ringo
import testutils

N_TOP_AUTHORS = 20
ENABLE_TIMER = True

if len(sys.argv) < 2:
  print """Usage: python use_case_2.py source [destination]
  source: input DBLP .tsv file
  destination: output .tsv file containing PageRank scores"""
  exit(1)
srcfile = sys.argv[1]
dstfile = sys.argv[2] if len(sys.argv) >= 3 else None

ringo = ringo.ringo()

t = testutils.Timer(ENABLE_TIMER)
S = {"Key":"string", "Author":"string"}
T = ringo.LoadTableTSV(S, srcfile)
t.show("load")

T2 = ringo.SelfJoin(T, "Key")
t.show("join")

ringo.Select(T2, "1_1.Author != 1_2.Author")
t.show("select")

G = ringo.ToGraph(T2, "1_1.Author", "1_2.Author")
t.show("graph")

P = ringo.PageRank(G)
t.show("page rank")

ringo.Order(P, ["PageRank"])
t.show("order")

if not dstfile is None:
  ringo.SaveTableTSV(P, dstfile)
  t.show("save")

# Print top authors with their PageRank score
T3 = ringo.Tables[P]
RI = T3.BegRI()
print "{0: <30}PageRank".format("Name")
print "-----------------------------------------"
cnt = 0
while RI < T3.EndRI() and cnt < N_TOP_AUTHORS:
  print "{0: <30}{1:.5f}".format(RI.GetStrAttr(ringo.NODE_ATTR_NAME), RI.GetFltAttr("PageRank"))
  RI.Next()
  cnt += 1
