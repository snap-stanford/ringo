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

	Tpull_merge = Tpull.SelfJoin("owner")
	print testutils.dump(Tpull_merge)

if __name__=="__main__":
	main(sys.argv[1:])
