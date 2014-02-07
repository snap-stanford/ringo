"""
Test case: Self Join on pull table's string columns.
Example: python github-join.py /dfs/ilfs2/0/ringo/GitHub/06-15-2012_11-16-2012/pull.tsv
"""

import sys
sys.path.append("..")
import os
import time
import snap
import testutils
import random

ENABLE_TIMER = True

def main(args):
	if len(args) < 1:
		print("python github-join.py <path_to_tsv_file>")
		sys.exit(1)

	filename = args[0]

	t = testutils.Timer(ENABLE_TIMER)
	context = snap.TTableContext()

	S = snap.Schema()
	S.Add(snap.TStrTAttrPr("userid", snap.atStr))
	S.Add(snap.TStrTAttrPr("owner", snap.atStr))
	S.Add(snap.TStrTAttrPr("name", snap.atStr))
	S.Add(snap.TStrTAttrPr("pullid", snap.atInt))
	S.Add(snap.TStrTAttrPr("status", snap.atStr))
	S.Add(snap.TStrTAttrPr("created_at", snap.atInt))
	Tpull = snap.TTable.LoadSS("Tpull", S, filename, context, '\t', snap.TBool(False))
	t.show("load pull")
	
	V = snap.TStrV()
	V.Add("created_at")
	Tpull.Order(V, "", snap.TBool(False), snap.TBool(True))

	V.Clr()		
	V.Add("owner")
	V.Add("name")
	V.Add("userid")
	Tpull.Group(V, "TagId")

	V.Clr()
	V.Add("TagId")
	Tpull.Unique(V)

	t.show("Unique")

	Tpull_merge = Tpull.SelfJoin("owner")
	t.show("Merge")

	# Things work fine till this point
	Tpull_merge.SelectAtomic("Tpull_1.name", "Tpull_2.name", snap.EQ)
	Tpull_merge.SelectAtomic("Tpull_1.pullid", "Tpull_2.pullid", snap.EQ)
	Tpull_merge.SelectAtomic("Tpull_1.userid", "Tpull_2.userid", snap.NEQ)
	Tpull_merge.ColMin("Tpull_1.created_at", "Tpull_2.created_at", "created_at")

	V = snap.TStrV()
	V.Add("Tpull_1.userid")
	V.Add("Tpull_2.userid")
	V.Add("created_at")
	Tpull_merge.ProjectInPlace(V)

	Tpull_merge.Rename("Tpull_1.userid", "userid1")
	Tpull_merge.Rename("Tpull_2.userid", "userid2")

	# Copy the Tpull_merge to form two graphs - base and delta. Select all rows in base for created_at < x and all dates in delta for created_at > x
	Tbase = snap.TTable.New(Tpull_merge, "Base")
	Tdelta = snap.TTable.New(Tpull_merge, "Delta")
	
	testutils.dump(Tpull_merge)

	x = 1342026109
	Tbase.SelectAtomicIntConst("created_at", x, snap.LTE)
	Tdelta.SelectAtomicIntConst("created_at", x, snap.GTE)

if __name__=="__main__":
	main(sys.argv[1:])
