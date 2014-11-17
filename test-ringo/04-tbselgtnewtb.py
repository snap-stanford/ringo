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

    table = ringo.Load(srcfile)
    t.show("load bin")
    r.show("__loadbin__")
    table2 = ringo.Select(table, "Src > 10000", False)

    t.show("selected > 10K new table")
    r.show("__selectedgt10Knewtable__")
