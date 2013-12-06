import os
import resource
import sys
import time

sys.path.append("../utils")

import snap
import testutils

#def Save(self,*args):
    #self().Save(*args)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <srcfile>"
        sys.exit(1)

    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Src", snap.atInt))
    schema.Add(snap.TStrTAttrPr("Dst", snap.atInt))
    table = snap.TTable.LoadSS("1", schema, srcfile, context, "\t", snap.TBool(False))
    t.show("load text", table)
    r.show("__loadtext__")

    Selected = snap.TIntV()
    table.SelectAtomicIntConst("Src", 10000, snap.LT, Selected, snap.TBool(False))
    table2 = snap.TTable.New(table, "2", Selected)
    t.show("selected < 10K new table", table2)
    r.show("__selectedlt10Knewtable__")

