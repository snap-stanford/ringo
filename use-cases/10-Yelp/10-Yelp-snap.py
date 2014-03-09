"""
 Use case #10: Find Yelp business that are within 500 kilometers of each other (Haversine <= 500)"
"""

import sys
sys.path.append("..")
import os
import time
import snap
import testutils

ENABLE_TIMER = True
DISTANCE_ATTRIBUTE = "HaversineDistance"

def get_usage():
	usage = "Usage: python 10-Yelp-snap.py <path/to/Yelp/business/file> output.tsv"
	return usage

def main(args):
	if len(args) < 3:
		print(get_usage())
		sys.exit(1)

	yelp = sys.argv[1]
	outFile = sys.argv[2]

	t = testutils.Timer(ENABLE_TIMER)
	context = snap.TTableContext()

	YelpS = snap.Schema()
	YelpS.Add(snap.TStrTAttrPr("Name", snap.atStr))
	YelpS.Add(snap.TStrTAttrPr("City", snap.atStr))
	YelpS.Add(snap.TStrTAttrPr("State", snap.atStr))
	YelpS.Add(snap.TStrTAttrPr("Latitude", snap.atFlt))
	YelpS.Add(snap.TStrTAttrPr("Longitude", snap.atFlt))

	TYelp = snap.TTable.LoadSS("Yelp", YelpS, yelp, context, '\t', snap.TBool(True));
	t.show("load Yelp", TYelp)

	Cols = snap.TStrV()
	Cols.Add("Latitude")
	Cols.Add("Longitude")

	# Get all business within 5 kilometers of each other
	JointTable = TYelp.SelfSimJoin(Cols, DISTANCE_ATTRIBUTE, snap.Haversine, 2)
	t.show("SimJoin complete", JointTable)

	ProjectionV = snap.TStrV()
	ProjectionV.Add("Yelp_1.Name")
	ProjectionV.Add("Yelp_1.City")
	ProjectionV.Add("Yelp_1.State")
	ProjectionV.Add("Yelp_2.Name")
	ProjectionV.Add("Yelp_2.City")
	ProjectionV.Add("Yelp_2.State")
	ProjectionV.Add(DISTANCE_ATTRIBUTE)

	JointTable.ProjectInPlace(ProjectionV)
	t.show("Project complete")

	testutils.dump(JointTable, 100);
	JointTable.SaveSS(outFile)

if __name__=="__main__":
	main(sys.argv)
