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

N_TOP_AUTHORS = 20
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

S3 = [("userid", "string"), ("owner", "string"), ("name", "string"), ("pullid", "string"), ("status", "string"), ("created_at", "int")]
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
t.show("merge collab", Tcollab_merge)

# If (u,v) worked on the same pull request on the same repository, they are added 
# as (soft) collaborators. 
Tpull_merge = ringo.SelfJoin(Tpull, "owner")
#print ringo.GetSchema(Tpull_merge)
ringo.Select(Tpull_merge, "3_1.name = 3_2.name", True)
ringo.Select(Tpull_merge, "3_1.pullid = 3_2.pullid", True)
Tpull_merge = ringo.ColMin(Tpull_merge, "3_1.created_at", "3_2.created_at", "created_at")
ringo.Project(Tpull_merge, ("3_1.userid", "3_2.userid", "created_at"))
t.show("merge pull", Tpull_merge)



# Convert to graphs
# >>> year = ringo.load('year.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("Key", snap.atStr))
S.Add(snap.TStrTAttrPr("Year", snap.atInt))
year = snap.TTable.LoadSS("2", S, yearFile, context, '\t', snap.TBool(False))
t.show("load year table", year)

# Select
# >>> year.select('Year >= 2005')
year.SelectAtomicIntConst("Year", 2005, snap.GTE)
t.show("select", year)

# Join
# >>> table = authors.join(year, ['Key'], ['Key'])
table = authors.Join("Key", year, "Key")
t.show("join", table)

# Self-join
# >>> table.selfjoin(table, ['Key'])
table = table.SelfJoin("Key")
t.show("join", table)

# Select
# >>> table.select('Author_1 != Author_2')
table.SelectAtomic("1_2_1.1.Author", "1_2_2.1.Author", snap.NEQ)
t.show("select", table)

# Create network
# >>> table.graph('Author_1', 'Author_2', directed=False)
table.SetSrcCol("1_2_1.1.Author")
table.SetDstCol("1_2_2.1.Author")
graph = table.ToGraph(snap.aaFirst)
t.show("graph", graph)

# Compute PageRank score
# >>> pagerank = graph.pageRank('PageRank')
HT = snap.TIntFltH()
snap.GetPageRank(graph, HT)
pagerank = snap.TTable.New("PR", HT, "Author", PAGE_RANK_ATTRIBUTE, context, snap.TBool(True))
t.show("page rank", pagerank)

# Order by PageRank score (in descending order)
# >>> pagerank.order(['PageRank'], desc = True)
V = snap.TStrV()
V.Add(PAGE_RANK_ATTRIBUTE)
pagerank.Order(V, "", snap.TBool(False), snap.TBool(False))
t.show("order", pagerank)

# Normalize PageRank scores so that the top score is 1
# >>> topPageRank = pagerank.first()['PageRank']
# >>> pagerank.arith('PageRank / {0}'.format(topPageRank))
topPageRank = pagerank.BegRI().GetFltAttr("PageRank")
pagerank.ColDiv("PageRank", topPageRank)
t.show("division", pagerank)

# Save final table
# >>> pagerank.save('table.tsv')
if not dstDir is None:
  pagerank.SaveSS(os.path.join(dstDir,OUTPUT_TABLE_FILENAME))
  t.show("save", pagerank)

# Print top authors with their PageRank score
testutils.dump(pagerank, N_TOP_AUTHORS)
