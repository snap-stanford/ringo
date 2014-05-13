# Tests the Union operation

import sys
sys.path.append("../use-cases")
import snap
import testutils
import pdb

P1 = snap.TStrTAttrPr("col1", snap.atInt)
P2 = snap.TStrTAttrPr("col2", snap.atInt)
S = snap.Schema()
S.Add(P1)
S.Add(P2)

Context = snap.TTableContext()
T1 = snap.TTable.LoadSS("1", S, "test2.tsv", Context)
testutils.dump(T1)

V = snap.TStrV()
V.Add("col1")
T2 = T1.Project(V, "2")
testutils.dump(T2)

V = snap.TStrV()
V.Add("col2")
T3 = T1.Project(V, "3")
testutils.dump(T3)

T3.Rename("col2","col1")
T4 = T2.Union(T3, "4")
testutils.dump(T4)

print "Rows in T1: %d" % T1.GetNumValidRows()
print "Rows in T2: %d" % T2.GetNumValidRows()
print "Rows in T3: %d" % T3.GetNumValidRows()
print "Rows in T4: %d" % T4.GetNumValidRows()
