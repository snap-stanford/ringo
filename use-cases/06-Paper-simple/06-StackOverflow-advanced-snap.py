"""
 Use case #6: Find experts with multiple skills in StackOverflow data
"""

import sys
sys.path.append("..")
sys.path.append("../../ringo-engine-python")
import os
import time
import snap
import testutils
import pdb

POSTS_FILE = 'posts.tsv'
TAGS_FILE = 'tags.tsv'
OUTPUT_TABLE_FILENAME = 'experts.tsv'
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

# Load posts
# >>> t1 = ringo.load('posts.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("UserId", snap.atInt))
S.Add(snap.TStrTAttrPr("AnswerId", snap.atInt))
S.Add(snap.TStrTAttrPr("Date", snap.atStr))
t1 = snap.TTable.LoadSS("t1", S, postsFile, context, '\t', snap.TBool(False))
t.show("load posts", t1)

# Load tags
# >>> t2 = ringo.load('tags.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("Tag", snap.atStr))
t2 = snap.TTable.LoadSS("t2", S, tagsFile, context, '\t', snap.TBool(False))
t.show("load tags", t2)

# Count
# >>> t2.Count('CommentScore', 'UserId')
t2.Count("Tag", "TagCount")
t.show("count", t2)

# Select
# >>> t.select('TagCount >= 10000')
t2.SelectAtomicIntConst("TagCount", 100000, snap.GTE)
t.show("select", t2)

# Join
# >>> t3 = t1.join(t2)
t3 = t1.Join("PostId", t2, "PostId")
t.show("join", t3)

# Join
# >>> t4 = t3.join(t1, ["AnswerId"], ["PostId"])
t4 = t3.Join("AnswerId", t1, "PostId")
t.show("join", t4)

# Graph sequence
# >>> t4.group()
# >>> g_seq = t4.graph("UserId_1", "UserId_2")
t4.SetSrcCol("t1_t2.t1.UserId")
t4.SetDstCol("t1.UserId")
V = snap.TStrV()
V.Add("t1_t2.t2.Tag")
t4.Group(V, "TagId")
graph_seq = t4.ToGraphPerGroup("TagId", snap.aaFirst) # ToGraphPerGroup should be able to support grouping on string columns!
table_seq = snap.TTable.GetMapHitsIterator(graph_seq, context)
t5 = None
count = 0
while table_seq.HasNext() and count <= 2:
  hits = table_seq.Next()
  V = snap.TStrV()
  V.Add("Authority")
  hits.Order(V, "", snap.TBool(False), snap.TBool(False))
  t.show("authority ordering", hits)
  V = snap.TStrV()
  V.Add("NodeId")
  hits.ProjectInPlace(V)
  t.show("authority project", hits)
  hits.SelectFirstNRows(100)
  t.show("authority first N", hits)
  if t5 is None:
    t5 = hits
  else:
    t5.UnionAllInPlace(hits)
    t.show("authority concat", t5)
  count += 1
t5.Reindex()
t5.Rename("NodeId", "UserId")

pdb.set_trace()
########## TODO: THERE IS A BUG AT THIS POINT (invalid table) ############

# Count
# >>> t5.Count('CommentScore', 'UserId')
# >>> t5.Unique()
t5.Count("UserId", "ExpertCount")
pdb.set_trace()
V = snap.TStrV()
V.Add("UserId")
t5.Unique(V)
t.show("count", t5)

pdb.set_trace()

# Select
# >>> t5.select('ExpertCount >= 5')
t5.SelectAtomicIntConst("ExpertCount", 5, snap.GTE)
t.show("select", t5)

# Project
# >>> t5 = t5.project(['UserId'])
V = snap.TStrV()
V.Add("UserId")
t5.ProjectInPlace(V)
t.show("project", t5)

# Save
if not destFile is None:
  t5.SaveSS(destFile)
  t.show("save", t5)

testutils.dump(t5)