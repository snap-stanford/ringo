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

    srcfile = sys.argv[1]

    ringo = ringo.Ringo()
    t = testutils.Timer()
    r = testutils.Resource()

    table = ringo.LoadTableBinary(srcfile)
    t.show("load bin")
    r.show("__loadbin__")

    ringo.Select(table, "Src > 10000")
    t.show("selected > 10K in place")
    r.show("__selectedgt10Kinplace__")
