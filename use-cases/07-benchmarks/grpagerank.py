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

    PRankH = snap.TIntFltH()

    # change the comments below to select the algorithm:
    #   GetPageRank() sequential
    #   GetPageRankMP1() parallel, non-optimized
    #   GetPageRankMP2() parallel, optimized
    #snap.GetPageRank(g, PRankH,  0.85, 1e-4, 100)
    #snap.GetPageRankMP1(g, PRankH,  0.85, 1e-4, 100)
    snap.GetPageRankMP2(g, PRankH,  0.85, 1e-4, 100)
    t.show("pagerank", g)
    r.show("__pagerank__")

    # comment out the line below to print out results
    sys.exit(0)

    count = 0
    l = [ (item.GetKey(), item.GetDat()) for item in PRankH ]
    print l[:10]
    for item in l:
        print "%8d %7f" % (item[0], item[1])
        count += 1
        if count > 20:
            break

    count = 0
    l.sort(key=lambda item: item[1], reverse=True)
    print l[:10]
    for item in l:
        print "%8d %7f" % (item[0], item[1])
        count += 1
        if count > 20:
            break

