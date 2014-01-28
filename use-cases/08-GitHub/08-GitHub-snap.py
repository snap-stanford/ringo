"""
 Use case #8: Recommend potential collaborators on GitHub using biased random walks with restarts. 
"""

import sys
sys.path.append("..")
import os
import time
import snap
import testutils
import utils

ENABLE_TIMER = True
OUTPUT_TABLE_FILENAME = "table.tsv"
PAGE_RANK_ATTRIBUTE = "PageRank"
NODE_ATTR_NAME = "__node_attr"


# Table file names 
TCOLLAB = 'collab.tsv'
TPULL = 'pull.tsv'
TREPO = 'repo.tsv'
TFOLLOW = 'followers.tsv'
TWATCH = 'watch.tsv'
TFORK = 'fork.tsv'

def GetSchema(T):
	Schema = T.GetSchema()
	S = []

	for Col in Schema:
		ColName = Col.Val1.CStr()
		ColType = Col.Val2
		S.append((ColName, ColType))

	return S

def get_usage():
	usage = """Usage: python 08-GitHub-snap.py <root> <outputdir>
	  Root directory should have the following files with the exact same names - 
		  %s - hard collaboration tsv file
		  %s - pull request tsv file
		  %s - repository tsv file
		  %s - followers tsv file
		  %s - repository watch tsv file
		  %s - repository fork tsv file
  outputdir: output directory"""%(TCOLLAB, TPULL, TREPO, TFOLLOW, TWATCH, TFORK)
	return usage


if len(sys.argv) < 2:
  	print(get_usage())
	sys.exit(1)

root = sys.argv[1]
dstDir = sys.argv[2] if len(sys.argv) > 2 else None

file_cache = {TCOLLAB:None, TPULL:None, TREPO:None, TFOLLOW:None, TWATCH:None, TFORK:None}

for file in os.listdir(root):
	if file.endswith(".tsv"):	
		file_cache[file] = os.path.join(root, file)
		print file_cache[file]

for key, val in file_cache.iteritems():
	if val==None:
		print("One of the required files not found.")
		print(get_usage())
		sys.exit(1)
		

if not dstDir is None:
  try:
    os.makedirs(dstDir)
  except OSError:
    pass

t = testutils.Timer(ENABLE_TIMER)
context = snap.TTableContext()

S1 = snap.Schema()
S1.Add(snap.TStrTAttrPr("userid1", snap.atStr))
S1.Add(snap.TStrTAttrPr("userid2", snap.atStr))
S1.Add(snap.TStrTAttrPr("created_at", snap.atInt))
Tfollow = snap.TTable.LoadSS("Tfollow", S1, file_cache[TFOLLOW], context, '\t', snap.TBool(False))
t.show("load follow")

S2 = snap.Schema()
S2.Add(snap.TStrTAttrPr("userid", snap.atStr))
S2.Add(snap.TStrTAttrPr("owner", snap.atStr))
S2.Add(snap.TStrTAttrPr("name", snap.atStr))
S2.Add(snap.TStrTAttrPr("created_at", snap.atInt))
Tcollab = snap.TTable.LoadSS("Tcollab", S2, file_cache[TCOLLAB], context, '\t', snap.TBool(False))
t.show("load collab")

S3 = snap.Schema()
S3.Add(snap.TStrTAttrPr("userid", snap.atStr))
S3.Add(snap.TStrTAttrPr("owner", snap.atStr))
S3.Add(snap.TStrTAttrPr("name", snap.atStr))
S3.Add(snap.TStrTAttrPr("pullid", snap.atInt))
S3.Add(snap.TStrTAttrPr("status", snap.atStr))
S3.Add(snap.TStrTAttrPr("created_at", snap.atInt))
Tpull = snap.TTable.LoadSS("Tpull", S3, file_cache[TPULL], context, '\t', snap.TBool(False))
t.show("load pull")

# If (u,v) collaborated on the same repository - determined by the owner, name pair,
# are added as collaborators. 
#TODO Better column renaming
Tcollab_merge = Tcollab.SelfJoin("owner")
Tcollab_merge.SelectAtomic("Tcollab_1.name", "Tcollab_2.name", snap.EQ)

# BUGBUG - Commenting this line will mean created_at is not present in Tcollab_merge. 
# However, the ProjectInPlace will not complain and silently exclude created_at from the
# result. This leads to the Index:-1 error in SelectAtomicIntConst on created_at later in the code. 
Tcollab_merge.ColMin("Tcollab_1.created_at", "Tcollab_2.created_at", "created_at")

V = snap.TStrV()
V.Add("Tcollab_1.userid")
V.Add("Tcollab_2.userid")
V.Add("created_at")
Tcollab_merge.ProjectInPlace(V)

Tcollab_merge.Rename("Tcollab_1.userid", "userid1")
Tcollab_merge.Rename("Tcollab_2.userid", "userid2")
t.show("merge collab", Tcollab_merge)

# If (u,v) worked on the same pull request on the same repository, they are added 
# as (soft) collaborators. 
Tpull_merge = Tpull.SelfJoin("owner")

Tpull_merge.SelectAtomic("Tpull_1.name", "Tpull_2.name", snap.EQ)
Tpull_merge.SelectAtomic("Tpull_1.pullid", "Tpull_2.pullid", snap.EQ)
Tpull_merge.ColMin("Tpull_1.created_at", "Tpull_2.created_at", "created_at")

V = snap.TStrV()
V.Add("Tpull_1.userid")
V.Add("Tpull_2.userid")
V.Add("created_at")
Tpull_merge.ProjectInPlace(V)

Tpull_merge.Rename("Tpull_1.userid", "userid1")
Tpull_merge.Rename("Tpull_2.userid", "userid2")
t.show("merge pull", Tpull_merge)

#BUGBUG: Toggle the two union calls (comment/Uncomment)- Then union method causes another error - NumRows==NumValidRows
#Tmerge = Tcollab_merge.Union(Tpull_merge, "Tmerge")
Tmerge = Tcollab_merge.UnionAll(Tpull_merge, "Tmerge")

# Remove self-loops from the table. 
Tmerge.SelectAtomic("userid1", "userid2", snap.NEQ)

# Select the base and delta tables from the merged table.
#Tbase = snap.TTable.New(Tmerge, "Base")
Tbase = Tmerge
Tbase.SelectAtomicIntConst("created_at", 10, snap.GTE)

#TODO: Union Tbase with collab and pull to include (userid, owner) edge
t.show("collab union")

# Convert base table to base graph
Tbase.SetSrcCol("userid1")
Tbase.SetDstCol("userid2")
Gbase = Tbase.ToGraph(snap.aaFirst)

HT = snap.TIntFltH()
snap.GetPageRank(Gbase, HT)

pagerank = snap.TTable.New("PR", HT, "Author", PAGE_RANK_ATTRIBUTE, context, snap.TBool(True))
t.show("base graph", Gbase)

V = snap.TStrV()
V.Add(PAGE_RANK_ATTRIBUTE)
pagerank.Order(V, "", snap.TBool(False), snap.TBool(False))
