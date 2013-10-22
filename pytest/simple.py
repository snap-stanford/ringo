import snap

P1 = snap.TStrIntPr("col1", 1)
P2 = snap.TStrIntPr("col2", 2)
S = snap.Schema()
S.Add(P1)
S.Add(P2)

Context = snap.TTableContext()
T = snap.TTable.LoadSS(1, S, "test.tsv", Context)

assert T.GetIntVal("col1",0) == 5 \
    and T.GetIntVal("col1",1) == 12 \
    and T.GetStrVal("col2",0) == "test" \
    and T.GetStrVal("col2",1) == "test2", \
    "Test error: TTable does not contain the expected data"
print "Test OK"
