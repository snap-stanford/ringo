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

    Selected = snap.TIntV()
    table.SelectAtomicIntConst("Src", 10000, snap.LT, Selected, snap.TBool(False))
    table2 = snap.TTable.New(table, "2", Selected)
    t.show("selected < 1000 new table", table2)
    r.show("__selectedlt1000newtable__")