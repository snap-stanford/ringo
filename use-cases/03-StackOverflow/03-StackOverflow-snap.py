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
  print """Usage: python 02-DBLP-snap.py <posts.tsv> <tags.tsv> <comments.tsv> <dest.tsv>
  posts.tsv: path to posts.tsv file
  tags.tsv: path to tags.tsv file
  comments.tsv: path to comments.tsv file
  dest.tsv: output .tsv file containing expert scores"""
  exit(1)
postsFile = sys.argv[1]
tagsFile = sys.argv[2]
commentsFile = sys.argv[3]
destFile = sys.argv[4] if len(sys.argv) >= 4 else None

#context = snap.TTableContext()

t = testutils.Timer(ENABLE_TIMER)

# a) Compute authority scores


# Load posts
# >>> posts = ringo.load('posts.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("UserId", snap.atInt))
S.Add(snap.TStrTAttrPr("AcceptedAnswerId", snap.atInt))
S.Add(snap.TStrTAttrPr("CreationDate", snap.atStr))
posts = snap.TTable.LoadSS("t1", S, postsFile, context, '\t', snap.TBool(False))
t.show("load posts", posts)

# Load tags
# >>> tags = ringo.load('tags.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
S.Add(snap.TStrTAttrPr("Tag", snap.atStr))
tags = snap.TTable.LoadSS("t2", S, tagsFile, context, '\t', snap.TBool(False))
t.show("load tags", tags)

# Select
# >>> tags.select('Tags = "python"')
tags.SelectAtomicStrConst("Tag", "python", snap.EQ)
t.show("select", tags)

# Join
# >>> questions = posts.join(tags)
questions = posts.Join("PostId", tags, "PostId")
t.show("join", questions)

# Project
# >>> questions.project(['PostId', 'UserId', 'AcceptedAnswerId'], in_place = True)
V = snap.TStrV()
V.Add("PostId")
V.Add("t1.UserId")
V.Add("t1.AcceptedAnswerId")
questions.ProjectInPlace(V)
t.show("copy & project", questions)

# Rename
# >>> questions.rename('UserId', 'Asker')
questions.Rename("t1.UserId", "Asker")
t.show("rename", questions)

# Project
# >>> posts.project(['PostId',UserId'], in_place = True)
V = snap.TStrV()
V.Add("PostId")
V.Add("UserId")
posts.ProjectInPlace(V)
t.show("project", posts)

# Rename
# >>> posts.rename('UserId','Expert')
posts.Rename("UserId", "Expert")
t.show("rename", posts)

# Join
# >>> edges = questions.join(posts, ['AcceptedAnswerId'], ['PostId'])
edges = questions.Join("t1.AcceptedAnswerId", posts, "PostId")
t.show("join", edges)

# Create haskell-specific Q&A graph
# >>> graph = posts.graph('Asker', 'Expert', directed = True)
edges.SetSrcCol("t1_t2.Asker")
edges.SetDstCol("t1.Expert")
graph = edges.ToGraph(snap.aaFirst)
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
comments = snap.TTable.LoadSS("comments", S, commentsFile, context, '\t', snap.TBool(False))
t.show("load", comments)

# Get table of all haskell related posts (both questions and answers)
# >>> taggedPosts = edges.union(edges, ['AcceptedAnswerId'], ['PostId'])
V = snap.TStrV()
V.Add("t1.PostId")
posts2 = edges.Project(V, "posts2")
posts2.Rename("t1.PostId", "Id")
V = snap.TStrV()
V.Add("t1.Expert")
posts3 = edges.Project(V, "posts3")
posts3.Rename("t1.Expert", "Id")
# TODO: There has to be a less painful way!
posts3.Rename("posts3_id", "posts2_id")
taggedPosts = posts2.Union(posts3, "tagged")
t.show("union", taggedPosts)

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
if not destFile is None:
  final.SaveSS(destFile)
  t.show("save", final)

testutils.dump(final, 20)
