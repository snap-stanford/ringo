import os
import resource
import sys
import time
import pdb

sys.path.append("../utils")

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
    for i in xrange(0,1):
        graph = table.ToPNGraphPar1()
        #graph = table.ToPNGraphPar()
        #graph = table.ToPNGraph()
        t.show("create graph", graph)
        r.show("__creategraph__")

    print "graph type", type(graph)

    table2 = snap.TTable.GetEdgeTablePN(graph, "1", context)
    t.show("table from graph", table2)
    r.show("__tablefromgraph__")

