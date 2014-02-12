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

t1 = ringo.LoadTableBinary('t1')
t3 = ringo.LoadTableBinary('t3')

# Join
t4 = ringo.Join(t3, t1, "AnswerId", "PostId")
t.show("join", t4)

# Graph
graph = ringo.ToGraph(t4, "1_2.1.UserId", "1.UserId")
t.show("graph", graph)
ringo.ShowMetadata(graph)

# Get authority scores
(HTHub, HTAuth) = ringo.GetHits(graph)
t.show("hits", graph)
ringo.ShowMetadata(HTAuth)

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
ringo.GenerateProvenance(t5, '06-StackOverflow-simple-autogen.py')
