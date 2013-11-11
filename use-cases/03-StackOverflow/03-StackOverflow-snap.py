"""
 Use case #3: Get a list of top Haskell experts
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
COMMENTS_FILE = 'comments.tsv'
OUTPUT_TABLE_FILENAME = 'table.tsv'
ENABLE_TIMER = True
AUTHORITY_ATTRIBUTE = "Authority"

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

context = snap.TTableContext()

t = testutils.Timer(ENABLE_TIMER)

# a) Compute authority scores

# Load posts
# >>> posts = ringo.load('posts.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("Id", snap.atInt))
S.Add(snap.TStrTAttrPr("ParentId", snap.atInt))
S.Add(snap.TStrTAttrPr("OwnerUserId", snap.atInt))
S.Add(snap.TStrTAttrPr("Score", snap.atInt))
S.Add(snap.TStrTAttrPr("Tags", snap.atStr))
posts = snap.TTable.LoadSS("posts", S, os.path.join(srcdir, POSTS_FILE), context, '\t', snap.TBool(False))
t.show("load posts", posts)

# Project
# >>> questions = posts.project(['Id', 'OwnerUserId', 'Tags'])
V = snap.TStrV()
V.Add("Id")
V.Add("OwnerUserId")
V.Add("Tags")
questions = posts.Project(V, "questions")
t.show("copy & project", questions)

# Rename
# >>> questions.rename('OwnerUserId', 'Asker')
questions.Rename("OwnerUserId", "Asker")
t.show("rename", questions)

# Select
# >>> questions.select('"haskell" in Tags')
questions.SelectAtomicStrConst("Tags", "python", snap.SUPERSTR)
t.show("select", questions)

# Project
# >>> posts.project(['Id',OwnerUserId','ParentId','Score'])
V = snap.TStrV()
V.Add("Id")
V.Add("OwnerUserId")
V.Add("ParentId")
V.Add("Score")
posts.ProjectInPlace(V)
t.show("project", posts)

# Rename
# >>> posts.rename('OwnerUserId','Expert')
posts.Rename("OwnerUserId", "Expert")
t.show("rename", posts)

# Join
# >>> posts = posts.join(questions, ['ParentId'], ['Id'])
posts = posts.Join("ParentId", questions, "Id")
t.show("join", posts)

# Create haskell-specific Q&A graph
# >>> graph = posts.graph('Asker', 'Expert', directed = True)
posts.SetSrcCol("Asker")
posts.SetDstCol("Expert")
graph = posts.ToGraph(snap.aaFirst)
t.show("graph", graph)

# Compute Authority score
# >>> hits = graph.hits('Authority', 'Hub')
# note: the code below creates a table (Node name, Authority score) - the hub score is not used
HTHub = snap.TIntFltH()
HTAuth = snap.TIntFltH()
snap.GetHits(graph, HTHub, HTAuth)
authority = snap.TTable.New("authority", HTAuth, "Expert", AUTHORITY_ATTRIBUTE, context, snap.TBool(False))
t.show("authority score", authority)

# b) Compute comment scores

# Load comments
# >>> comments = ringo.load('comments.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("UserId", snap.atInt))
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
comments = snap.TTable.LoadSS("comments", S, os.path.join(srcdir, COMMENTS_FILE), context, '\t', snap.TBool(False))
t.show("load", comments)

# Get table of all haskell related posts (both questions and answers)
# >>> taggedPosts = posts.union(posts, ['Id'], ['ParentId'])
# Note: actually this operation is not necessary
V = snap.TStrV()
V.Add("questions.Id")
posts2 = posts.Project(V, "posts2")
posts2.Rename("questions.Id", "Id")
V = snap.TStrV()
V.Add("posts.Id")
posts3 = posts.Project(V, "posts3")
posts3.Rename("posts.Id", "Id")
# TODO: There has to be a less painful way!
posts3.Rename("posts3_id", "posts2_id")
taggedPosts = posts2.Union(posts3, "tagged")
t.show("union", taggedPosts)

# Unique
# >>> taggedPosts.Unique(["Id"])
V = snap.TStrV()
V.Add("Id")
taggedPosts.Unique(V)
t.show("unique", taggedPosts)

# Join
# >>> comments = comments.join(taggedPosts, ['PostId'], ['Id'])
comments = comments.Join("PostId", taggedPosts, "Id")
comments.Rename("comments.UserId", "UserId")
t.show("join", comments)

# Count
# >>> comments.Count('CommentScore', 'UserId')
# >>> comments.Unique()
comments.Count("NumComments", "UserId")
V = snap.TStrV()
V.Add("UserId")
V.Add("NumComments")
comments.Unique(V)
t.show("count", comments)

# Divide number of comments by total number of comments
# >>> totalComments = comments.GetNumRows()
# >>> comments.arith('CommentScore / {0}'.format(totalComments))
totalComments = comments.GetNumValidRows()
comments.ColDiv("NumComments", totalComments, "CommentScore", snap.TBool(True))
t.show("division", comments)

# Project
# >>> posts.project(['OwnerUserId','ParentId','Score'])
V = snap.TStrV()
V.Add("UserId")
V.Add("CommentScore")
comments.ProjectInPlace(V)
t.show("project", comments)

# b) Combine authority and comment scores

# Join
# >>> comments = comments.join(authority, ['UserId'], ['Expert'])
final = comments.Join("UserId", authority, "Expert")
t.show("join", final)

# Multiply authority and comment scores
# >>> final.arith('Authority * CommentScore', 'FinalScore')
final.ColMul("Authority", "CommentScore", "FinalScore")
t.show("division", final)

# Order by final score (in descending order)
# >>> rank.order(['FinalScore'], desc = True)
V = snap.TStrV()
V.Add("FinalScore")
final.Order(V, "", snap.TBool(False), snap.TBool(False))
t.show("order", final)

# Save
# Save final table
# >>> rank.save('table.tsv')
# Rename columns and remove unnecessary ones before saving
final.Rename("authority.Expert", "Expert")
final.Rename("comments_tagged.CommentScore", "CommentScore")
final.Rename("authority.Authority", "Authority")
V = snap.TStrV()
V.Add("Expert")
V.Add("FinalScore")
final.ProjectInPlace(V)
if not dstdir is None:
  final.SaveSS(os.path.join(dstdir,OUTPUT_TABLE_FILENAME))
  t.show("save", final)

testutils.dump(final, 20)
