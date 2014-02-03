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
import random

ENABLE_TIMER = True
PAGE_RANK_ATTRIBUTE = "PageRank"
NODE_ATTR_NAME = "__node_attr"
N_TOP_RECOS = 20
ALPHA=0.3  # Random walk with restart jump probability

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
	usage = """Usage: python 08-GitHub-snap.py <root> <mid_date>
	  Root directory should have the following files with the exact same names - 
		  %s - hard collaboration tsv file
		  %s - pull request tsv file
		  %s - repository tsv file
		  %s - followers tsv file
		  %s - repository watch tsv file
		  %s - repository fork tsv file
  	 mid_date: Date to separate base and delta graphs."""%(TCOLLAB, TPULL, TREPO, TFOLLOW, TWATCH, TFORK)

	return usage


if len(sys.argv) < 3:
  	print(get_usage())
	sys.exit(1)

root = sys.argv[1]
mid_date = sys.argv[2]
mid_ticks = utils.date_to_ticks(mid_date)

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
Tbase = snap.TTable.New(Tmerge, "Base")
Tdelta = snap.TTable.New(Tmerge, "Delta")

#TODO: Replace 10 with mid-date
Tbase.SelectAtomicIntConst("created_at", mid_ticks, snap.LTE)
Tdelta.SelectAtomicIntConst("created_at", mid_ticks, snap.GTE)

#TODO: Union Tbase with collab and pull to include (userid, owner) edge
t.show("collab union")

# Convert base table to base graph
Tbase.SetSrcCol("userid1")
Tbase.SetDstCol("userid2")
Gbase = Tbase.ToGraph(snap.aaFirst)

Tdelta.SetSrcCol("userid1")
Tdelta.SetDstCol("userid2")
Gdelta = Tdelta.ToGraph(snap.aaFirst)


NITERS = 20
total_preck = 0

print("Userid\tPrec@%d\tAverage Index"%(N_TOP_RECOS))

# Random walk with restarts
# BUGBUG: Returns the same id everytime
# userid = Gbase.GetRndNId()
for i in range(NITERS):
	# Randomly choose a starting node
	userid = random.choice([node.GetId() for node in Gbase.Nodes()])
	user = Gbase.GetNI(userid)

	# Perform random walk with restarts on base graph
	HT = snap.TIntFltH()
	snap.GetRndWalkRestart_PNEANet(Gbase, ALPHA, userid, HT)
	HT.SortByDat(False)

	i = 0
	cnt = 0
	preck = 0
	average_index = -1

	# Calculate precision
	while cnt<N_TOP_RECOS and i<HT.Len():
		recoid = HT.GetKey(i)
		pagerank = HT.GetDat(recoid)
		
		#print recoid, pagerank

		if recoid!=userid:
			# If the edge is not in base graph but is present in delta graph, we made an accurate prediction.
			if not Gbase.IsEdge(userid, recoid) and Gdelta.IsNode(userid) and Gdelta.IsNode(recoid) and (Gdelta.IsEdge(userid, recoid) or Gdelta.IsEdge(recoid, userid)):
				preck += 1		

			cnt += 1	
		i+=1

	# Calculate average index
	try:
		node = Gdelta.GetNI(userid)
		edges = [nid for nid in node.GetOutEdges()] + [nid for nid in node.GetInEdges()]
		index = 0

		for nid in edges:
			index+= HT.GetKeyId(nid)
		
		average_index = index/len(edges)
	except:
		# Node not present in delta graph implies no new edges formed
		pass	
	
	total_preck += preck
	print("%d\t%d\t%f"%(userid, preck, average_index))

	#rank = snap.TTable.New("Rank", HT, "User", PAGE_RANK_ATTRIBUTE, context, snap.TBool(True))
print("Average Precision@%d = %f" %(N_TOP_RECOS, total_preck/float(NITERS)))
# testutils.dump(rank)
