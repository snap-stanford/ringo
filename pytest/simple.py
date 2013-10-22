import snap

P1 = snap.TStrIntPr("col1", 1)
P2 = snap.TStrIntPr("col2", 2)
S = snap.Schema()
S.Add(P1)
S.Add(P2)

Context = snap.TTableContext()
T = snap.TTable.LoadSS(1, S, "test.tsv", Context)

data = [T.GetIntVal("col1",0), \
    T.GetIntVal("col1",1), \
    T.GetStrVal("col2",0), \
    T.GetStrVal("col2",1)]
print "Data: " + str(data)
if not data == [5, 12, "test", "test2"]:
  print "Test error"
else:
  print "Test OK"
