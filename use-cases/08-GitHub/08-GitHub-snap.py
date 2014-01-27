"""
 Use case #8: Recommend potential collaborators on GitHub using biased random walks with restarts. 
"""

import sys
sys.path.append("..")
sys.path.append("../../ringo-engine-python")
import os
import time
import snap
import testutils
import ringo
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

context = snap.TTableContext()
t = testutils.Timer(ENABLE_TIMER)

ringo = ringo.Ringo()

# Load data
# >>> authors = ringo.load('authors.tsv')
S1 = [("userid1", "string"), ("userid2", "string"), ("created_at", "int")]
Tfollow = ringo.LoadTableTSV(S1, file_cache[TFOLLOW])
t.show("load follow")

# UserId, Owner of Repo, Name of repo, created_at => (owner, name) uniquely identies a repo
S2 = [("userid", "string"), ("owner", "string"), ("name", "string"), ("created_at", "int")]
Tcollab = ringo.LoadTableTSV(S2, file_cache[TCOLLAB])
t.show("load collab")

S3 = [("userid", "string"), ("owner", "string"), ("name", "string"), ("pullid", "int"), ("status", "string"), ("created_at", "int")]
Tpull = ringo.LoadTableTSV(S3, file_cache[TPULL])
t.show("load pull")

Tfork = ringo.LoadTableTSV(S2, file_cache[TFORK])
t.show("load fork")

Twatch = ringo.LoadTableTSV(S2, file_cache[TWATCH])
t.show("load watch")

# If (u,v) collaborated on the same repository - determined by the owner, name pair,
# are added as collaborators. 
#TODO Better column renaming

Tcollab_merge = ringo.SelfJoin(Tcollab, "owner")
ringo.Select(Tcollab_merge, "2_1.name = 2_2.name", True)
Tcollab_merge = ringo.ColMin(Tcollab_merge, "2_1.created_at", "2_2.created_at", "created_at")
ringo.Project(Tcollab_merge, ("2_1.userid", "2_2.userid", "created_at"))
ringo.Rename(Tcollab_merge, "2_1.userid", "userid1")
ringo.Rename(Tcollab_merge, "2_2.userid", "userid2")
t.show("merge collab", Tcollab_merge)

# If (u,v) worked on the same pull request on the same repository, they are added 
# as (soft) collaborators. 
Tpull_merge = ringo.SelfJoin(Tpull, "owner")
ringo.Select(Tpull_merge, "3_1.name = 3_2.name", True)
ringo.Select(Tpull_merge, "3_1.pullid = 3_2.pullid", True)
Tpull_merge = ringo.ColMin(Tpull_merge, "3_1.created_at", "3_2.created_at", "created_at")
ringo.Project(Tpull_merge, ("3_1.userid", "3_2.userid", "created_at"))
ringo.Rename(Tpull_merge, "3_1.userid", "userid1")
ringo.Rename(Tpull_merge, "3_2.userid", "userid2")
t.show("merge pull", Tpull_merge)

Tmerge = ringo.UnionAll(Tcollab_merge, Tpull_merge, "collab")
# Remove self-loops from the table. 
ringo.Select(Tmerge, "userid1 != userid2")

# Select the base and delta tables from the merged table.
Tbase = ringo.Select(Tmerge, "created_at >= 10", False, True)

#TODO: Iterate over the rows and add (userid, owner) edge
t.show("collab union")

# Convert base table to base graph
Gbase = ringo.ToGraph(Tbase, "userid1", "userid2")
t.show("base graph", Gbase)

TPageRank = ringo.PageRank(Gbase)
ringo.DumpTableContent(TPageRank)
