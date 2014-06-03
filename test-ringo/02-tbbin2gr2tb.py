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
    
    table = ringo.Load(srcfile)
    t.show("load bin")
    r.show("__loadbin__")

    S = map(lambda x: x[0], ringo.GetSchema(table))
    assert(len(S) >= 2)

    G = ringo.ToGraph(ringo.PNGraph, table, S[0], S[1])
    t.show("create graph")
    r.show("__creategraph__")
    #table2 = ringo.GetEdgeTable(G)
    t.show("table from graph")
    r.show("__tablefromgraph__")

    G.GenerateProvenance('provenance_scripts/02.py')