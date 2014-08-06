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

    tall = testutils.Timer()
    rall = testutils.Resource()

    for i in xrange(0,10):

        cnt = snap.CountTriangles(g)
        print cnt
        t.show("tri1")
        r.show("__tri1__")

    tall.show("tri1all", g)
    rall.show("__tri1all__")

    for i in xrange(0,10):

        cnt = snap.GetTriangleCnt(g)
        print cnt
        t.show("tri2")
        r.show("__tri2__")

    tall.show("tri2all", g)
    rall.show("__tri2all__")

