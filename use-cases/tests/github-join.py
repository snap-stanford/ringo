"""
Test case: Self Join on pull table's string columns.
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
		print(get_usage())
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

	print("Staring Self Join")
	Tpull_merge = Tpull.SelfJoin("owner")
	t.show("merge pull", Tpull_merge)

if __name__=="__main__":
	main(sys.argv[1:])
