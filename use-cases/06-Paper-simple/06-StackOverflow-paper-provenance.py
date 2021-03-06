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
S = [('PostId','int'), ('UserId','int'), ('AnswerId','int'), ('CreationDate', 'string')]
POSTS = ringo.LoadTableTSV(S, os.path.join(srcdir, POSTS_FILE))
t.show("load posts", POSTS)

# Load tags
S = [('PostId','int'), ('Tag','string')]
T = ringo.LoadTableTSV(S, os.path.join(srcdir, TAGS_FILE))
t.show("load tags", T)

# Join
P = ringo.Join(POSTS, T, "PostId", "PostId")
t.show("join", P)

# Select Java posts
print ringo.GetSchema(P)
ringo.Select(P, '2.Tag = java', CompConstant = True)
t.show("select", P)

# Select Questions
Q = ringo.Select(P, '1.AnswerId != 0', InPlace = False, CompConstant = True)
t.show("select", Q)

# Select Answers
A = ringo.Select(P, '1.AnswerId = 0', InPlace = False, CompConstant = True)
t.show("select", A)

#print ringo.DumpTableContent(Q,5)
#print ringo.DumpTableContent(A,5)
#ringo.GenerateProvenance(Q, '06-StackOverflow-paper-autogen-Q.py')
#ringo.GenerateProvenance(A, '06-StackOverflow-paper-autogen-A.py')
# Join
QA = ringo.Join(Q, A, "1.AnswerId", "1.PostId")
t.show("join", QA)

print ringo.GetSchema(QA)
# Graph
graph = ringo.ToGraph(QA, "1.1.UserId", "2.1.UserId")
t.show("graph", graph)
ringo.GenerateProvenance(graph, '06-StackOverflow-paper-autogen.py')
