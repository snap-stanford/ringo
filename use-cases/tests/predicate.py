import sys
import snap
sys.path.append("..")
import testutils

def main():
	S = snap.Schema()
	context = snap.TTableContext()

	S.Add(snap.TStrTAttrPr("Animal", snap.atStr))
	S.Add(snap.TStrTAttrPr("Size", snap.atStr))
	S.Add(snap.TStrTAttrPr("Location", snap.atStr))
	S.Add(snap.TStrTAttrPr("Number", snap.atInt))
	Animals = snap.TTable.LoadSS("Animals", S, "/dfs/ilfs2/0/ringo/tests/animals.txt", context, '\t', snap.TBool(False))

	# Gets animals with size=big
	pred_size = snap.TAtomicPredicate(snap.atStr, snap.TBool(True), snap.EQ, "Size", "", 0, 0, "big")
	node_size = snap.TPredicateNode(pred_size)

	# Get animals with location=Australia
	pred_location = snap.TAtomicPredicate(snap.atStr, snap.TBool(True), snap.EQ, "Location", "", 0, 0, "Australia")
	node_location = snap.TPredicateNode(pred_location)

	# size=big and location=Australia
	node1 = snap.TPredicateNode(snap.AND)
	node1.AddLeftChild(node_size)
	node1.AddRightChild(node_location)

	# Get animals with name==location (fabricated to show a non const case
	pred_animal_location = snap.TAtomicPredicate(snap.atStr, snap.TBool(False), snap.EQ, "Animal","Location")
	node2 = snap.TPredicateNode(pred_animal_location)

	# (size=big and location=Australia) or Animal==Location
	node_root = snap.TPredicateNode(snap.OR)
	node_root.AddLeftChild(node1)
	node_root.AddRightChild(node2)
	pred = snap.TPredicate(node_root)

	Animals.Select(pred)
	testutils.dump(Animals)

if __name__=="__main__":
	main()
