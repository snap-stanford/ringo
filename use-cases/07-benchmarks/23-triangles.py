import sys
import os
import time

sys.path.append("../utils")

import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <graph>"
        sys.exit(1)

    srcfile = sys.argv[1]

    t = testutils.Timer()
    r = testutils.Resource()

    FIn = snap.TFIn(srcfile)
    g = snap.TNGraph.Load(FIn) 
    t.show("load graph", g)
    r.show("__loadbin__")

    cnt = snap.CountTriangles(snap.PNGraph, g)
    print cnt
    t.show("triangles")
    r.show("__triangles__")
