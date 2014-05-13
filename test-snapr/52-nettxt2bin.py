import os
import resource
import sys
import time

sys.path.append("../utils")

import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <srcfile> <dstfile>"
        sys.exit(1)

    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    t = testutils.Timer()
    r = testutils.Resource()

    g = snap.LoadEdgeList(snap.PNEANet, srcfile, 0, 1)
    t.show("load text", g)
    r.show("__loadtext__")

    FOut = snap.TFOut(dstfile)
    g.Save(FOut)
    FOut.Flush()
    t.show("save bin", g)
    r.show("__savebin__")

