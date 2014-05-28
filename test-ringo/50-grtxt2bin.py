import os
import resource
import sys
import time

sys.path.append("../utils")
sys.path.append("../ringo-engine-python")
import ringo
import snap
import testutils

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <srcfile> <dstfile>"
        sys.exit(1)

    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    ringo = ringo.Ringo()

    t = testutils.Timer()
    r = testutils.Resource()
    
    g = ringo.LoadEdgeList(ringo.PNGraph, srcfile, 0, 1)
    t.show("load text")
    r.show("__loadtext__")

    ringo.SaveEdgeList(g, dstfile)
    t.show("save bin")
    r.show("__savebin__")
