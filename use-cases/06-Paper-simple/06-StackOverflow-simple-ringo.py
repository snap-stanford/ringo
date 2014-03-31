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
import ringo

POSTS_FILE = 'posts.tsv'
TAGS_FILE = 'tags.tsv'
OUTPUT_TABLE_FILENAME = 'experts.tsv'
ENABLE_TIMER = True

if len(sys.argv) < 2:
  print """Usage: python 02-DBLP-snap.py source [destination]
  srcDir: input directory containing posts.tsv and comments.tsv files
  destination: output .tsv file containing expert scores"""
  exit(1)
srcdir = sys.argv[1]
dstdir = sys.argv[2] if len(sys.argv) >= 3 else None
if not dstdir is None:
  try:
    os.makedirs(dstdir)
  except OSError:
    pass

ringo = ringo.Ringo()

t = testutils.Timer(ENABLE_TIMER)

# Load posts
S = [('PostId','int'), ('UserId','int'), ('AnswerId','int'), ('CreationDate','string')]
t1 = ringo.LoadTableTSV(S, os.path.join(srcdir, POSTS_FILE))
t.show("load posts", t1)

# Load tags
S = [('PostId','int'), ('Tag','string')]
t2 = ringo.LoadTableTSV(S, os.path.join(srcdir, TAGS_FILE))
t.show("load tags", t2)

# Select
ringo.Select(t2, 'Tag = python', CompConstant = True)
t.show("select", t2)

# Join
t3 = ringo.Join(t1, t2, 'PostId', 'PostId')
t.show("join", t3)

# Join
t4 = ringo.Join(t3, t1, "AnswerId", "PostId")
t.show("join", t4)

# Graph
graph = ringo.ToGraph(t4, "1_2.1.UserId", "1.UserId")
t.show("graph", graph)

# Get authority scores
(HTHub, HTAuth) = ringo.GetHits(graph)
HT = ringo.GetHits(graph)
t.show("hits", graph)

t5 = ringo.TableFromHashMap(HTAuth, "UserId", "Authority")
t.show("authority score", t5)

# Select top entries
#ringo.Select(t5, 'Authority > 0.0', CompConstant = True)
#t.show("select", t5)

# Order by final score (in descending order)
ringo.Order(t5, ['Authority'], Asc = False)
t.show("order", t5)

# Save
if not dstdir is None:
  ringo.SaveTableTSV(t5, os.path.join(dstdir,OUTPUT_TABLE_FILENAME))
  t.show("save", t5)

ringo.DumpTableContent(t5, 20)
ringo.ShowMetadata(t5)
ringo.ShowDependencies(t5)
ringo.ShowDependencies(t5, True)

