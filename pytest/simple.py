import snap

P1 = snap.TStrIntPr("col1", 1)
P2 = snap.TStrIntPr("col2", 2)
S = snap.Schema()
S.Add(P1)
S.Add(P2)

Context = snap.TTableContext()
T = snap.TTable.LoadSS(1, S, "test.tsv", Context)

