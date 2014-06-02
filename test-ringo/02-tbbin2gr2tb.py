import os
import resource
import sys
import time
import pdb

sys.path.append("../utils")
sys.path.append("../ringo-engine-python")
import ringo
import snap
import testutils

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <srcfile>"
        sys.exit(1)

    ringo = ringo.Ringo()
    srcfile = sys.argv[1]

    t = testutils.Timer()
    r = testutils.Resource()
    
    table = ringo.LoadTableBinary(srcfile)
    t.show("load bin")
    r.show("__loadbin__")

    S = map(lambda x: x[0], ringo.GetSchema(table))
    assert(len(S) >= 2)

    G = ringo.ToGraph(table, S[0], S[1])
    t.show("create graph")
    r.show("__creategraph__")
    # Ringo? table2 = snap.TTable.GetEdgeTable(graph, context)
    t.show("table from graph")
    r.show("__tablefromgraph__")
