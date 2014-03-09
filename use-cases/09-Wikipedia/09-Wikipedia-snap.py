"""
 Use case #9: Find Wikipedia users who have voted similar candidates (Jaccard distance <= 0.5)
"""

import sys
sys.path.append("..")
import os
import time
import snap
import testutils

ENABLE_TIMER = True
DISTANCE_ATTRIBUTE = "JaccardDistance"

def get_usage():
	usage = "Usage: python 09-Wikipedia-snap.py <path/to/wikipedia/votes/file> output.tsv"
	return usage

def main(args):
	if len(args) < 3:
		print(get_usage())
		sys.exit(1)

	votes = sys.argv[1]
	outFile = sys.argv[2]

	t = testutils.Timer(ENABLE_TIMER)
	context = snap.TTableContext()

	VoteS = snap.Schema()
	VoteS.Add(snap.TStrTAttrPr("UserId", snap.atInt))
	VoteS.Add(snap.TStrTAttrPr("AdminId", snap.atInt))
	TVotes = snap.TTable.LoadSS("WikiVotes", VoteS, votes, context, '\t', snap.TBool(False))
	t.show("load Votes", TVotes)

	GroupBy = snap.TStrV()
	GroupBy.Add("UserId")
	JointTable = TVotes.SelfSimJoinPerGroup(GroupBy, "AdminId", DISTANCE_ATTRIBUTE, snap.Jaccard, 0.5)
	t.show("SimJoinPerGroup complete", JointTable)

	JointTable.SelectAtomic("WikiVotes_1.UserId", "WikiVotes_2.UserId", snap.NEQ)
	t.show("Select complete", JointTable)

	testutils.dump(JointTable, 20);
	JointTable.SaveSS(outFile)

if __name__=="__main__":
	main(sys.argv)
