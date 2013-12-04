"""
 Use case #6: Find top python experts in StackOverflow data
 This variant directly reads the tables form .xml files
"""

import sys
sys.path.insert(1, "../utils")
sys.path.append("../../ringo-engine-python")
import os
import time
import snap
import testutils
import tableutils
from lxml import etree
import pdb

ENABLE_TIMER = True

if len(sys.argv) < 2:
  print """Usage: python 06-StackOverflow-simple-snap.py <posts.xml> <dest.tsv>
  posts.xml: path to posts.xml file
  dest.tsv: output .tsv file containing expert scores"""
  exit(1)
postsFile = sys.argv[1]
destFile = sys.argv[2] if len(sys.argv) >= 3 else None

context = snap.TTableContext()

t = testutils.Timer(ENABLE_TIMER)

# a) Compute authority scores

# Load posts (directly from parser)
# >>> t1 = ringo.load('posts.xml')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("UserId", snap.atInt))
S.Add(snap.TStrTAttrPr("AnswerId", snap.atInt))
S.Add(snap.TStrTAttrPr("CreationDate", snap.atStr))
t1 = snap.TTable.New(snap.TStr("t1"), S, context)
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("Tag", snap.atStr))
t2 = snap.TTable.New(snap.TStr("t2"), S, context)
count = 0
unicode_failures = 0
missing_info = 0
with open(postsFile) as source:
  context = etree.iterparse(source)
  for event, element in context:
    try:
      if element.tag == 'row':
        postId = element.get('Id')
        userId = element.get('OwnerUserId')
        answerId = element.get('AcceptedAnswerId')
        creationDate = element.get('CreationDate')
        if postId is None or userId is None or creationDate is None:
          missing_info += 1
          continue
        if answerId is None:
          answerId = "0"
        tableutils.addRow(t1, (int(postId), int(userId), int(answerId), creationDate))
        tags = element.get('Tags')
        if not tags is None:
          tags = tags[1:-1].split('><')
          for tag in tags:
            tableutils.addRow(t2, (int(postId), tag))
      count += 1
      if not N is None and count >= N:
        break
      if count % 10000 == 0:
        print count
    except UnicodeEncodeError:
      unicode_failures += 1
    element.clear()
t1.InitIds()
t2.InitIds()
t.show("load posts", t1)
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
t4 = t3.Join("AnswerId", t1, "PostId")
t.show("join", t4)

# Graph
# >>> graph = t4.graph("UserId_1", "UserId_2")
t4.SetSrcCol("t1_t2.t1.UserId")
t4.SetDstCol("t1.UserId")
graph = t4.ToGraph(snap.aaFirst) # ToGraphPerGroup should be able to support grouping on string columns!
t.show("graph", graph)
graph.Dump()

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
