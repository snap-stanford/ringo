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

    table2 = snap.TTable.New("2", table.GetSchema(), context)
    table.SelectAtomicIntConst("Src", 10000, snap.LT, table2)
    t.show("selected < 10K new table", table2)
    r.show("__selectedlt10Knewtable__")

