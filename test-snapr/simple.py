import snap

P1 = snap.TStrTAttrPr("col1", snap.atInt)
P2 = snap.TStrTAttrPr("col2", snap.atStr)
S = snap.Schema()
S.Add(P1)
S.Add(P2)

Context = snap.TTableContext()
T = snap.TTable.LoadSS("1", S, "test.tsv", Context)

c10 = T.GetIntVal("col1",0)
c11 = T.GetIntVal("col1",1)
c20 = T.GetStrVal("col2",0)
c21 = T.GetStrVal("col2",1)

print "c10 %d, c11 %d, c20 %s, c21 %s" % (c10, c11, c20, c21)

if c10 != 5  or  c11 != 12  or  c20 != "test"  or c21 != "test2":
  print "Test error"
else:
  print "Test OK"

