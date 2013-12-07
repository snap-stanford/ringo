import os
import resource
import sys
import time
import pdb

sys.path.append("../utils")
sys.path.insert(0, "../../swig")

import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <srcfile>"
        sys.exit(1)

    srcfile = sys.argv[1]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    FIn = snap.TFIn(srcfile)
    table = snap.TTable.Load(FIn, context)
    t.show("load bin", table)
    r.show("__loadbin__")

    S = map(lambda x: x.GetVal1(), table.GetSchema())
    assert(len(S) >= 2)
    table.SetSrcCol(S[0])
    table.SetDstCol(S[1])
    graph = table.ToGraphDirected(snap.aaFirst)
    t.show("create graph", table)
    r.show("__creategraph__")

    #table2 = snap.TTable.GetEdgeTable(graph, "1", context)
    #t.show("table from graph", table2)
    #r.show("__tablefromgraph__")

    print graph.GetNodes(), graph.GetEdges()