"""
 Use case #6: Find top python experts in StackOverflow data
"""

import sys
sys.path.insert(1, "..")
sys.path.append("../../ringo-engine-python")
import os
import time
import snap
import testutils
import pdb

ENABLE_TIMER = True

if len(sys.argv) < 2:
  print """Usage: python 06-StackOverflow-simple-snap.py <posts.tsv> <tags.tsv> <dest.tsv>
  posts.tsv: path to posts.tsv file
  tags.tsv: path to tags.tsv file
  dest.tsv: output .tsv file containing expert scores"""
  exit(1)
postsFile = sys.argv[1]
tagsFile = sys.argv[2]
destFile = sys.argv[3] if len(sys.argv) >= 4 else None

context = snap.TTableContext()

t = testutils.Timer(ENABLE_TIMER)

# a) Compute authority scores

# Load posts
# >>> t1 = ringo.load('posts.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("UserId", snap.atInt))
S.Add(snap.TStrTAttrPr("AnswerId", snap.atInt))
S.Add(snap.TStrTAttrPr("CreationDate", snap.atStr))
t1 = snap.TTable.LoadSS("t1", S, postsFile, context, '\t', snap.TBool(False))
t.show("load posts", t1)

# Load tags
# >>> t2 = ringo.load('tags.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("Tag", snap.atStr))
t2 = snap.TTable.LoadSS("t2", S, tagsFile, context, '\t', snap.TBool(False))
t.show("load tags", t2)

# Select
# >>> t.select('Tag = "python"'')
t2.SelectAtomicStrConst("Tag", "python", snap.EQ)
t.show("select", t2)

# Join
# >>> t3 = t1.join(t2)
t3 = t1.Join("PostId", t2, "PostId")
t.show("join", t3)

# Join
# >>> t4 = t3.join(t1, ["AnswerId"], ["PostId"])
t4 = t3.Join("t1.AnswerId", t1, "PostId")
t.show("join", t4)

# Graph
# >>> graph = t4.graph("UserId_1", "UserId_2")
#t4.SetSrcCol("t1_t2.t1.UserId")
#t4.SetDstCol("t1.UserId")
graph = snap.ToGraph(snap.PNGraph, t4, "t1_t2.t1.UserId", "t1.UserId", snap.aaFirst) # ToGraphPerGroup should be able to support grouping on string columns!
t.show("graph", graph)
#graph.Dump()

# Get authority scores
HTHub = snap.TIntFltH()
HTAuth = snap.TIntFltH()
snap.GetHits(graph, HTHub, HTAuth)
t.show("hits", graph)

t5 = snap.TTable.TableFromHashMap("t5", HTAuth, "UserId", "Authority", context, snap.TBool(False))
t.show("authority score", t5)

# Select top entries
# >>> t.select('Authority > 0.0')
#t5.SelectAtomicFltConst("Authority", 0.0, snap.GT)
#t.show("select", t5)

# Order by final score (in descending order)
# >>> t5.order(['Authority'], desc = True)
V = snap.TStrV()
V.Add("Authority")
t5.Order(V, "", snap.TBool(False), snap.TBool(False))
t.show("order", t5)

# Save
if not destFile is None:
  t5.SaveSS(destFile)
  t.show("save", t5)

testutils.dump(t5, 20)
