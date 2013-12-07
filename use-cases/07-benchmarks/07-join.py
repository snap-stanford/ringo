import os
import resource
import sys
import time
import pdb

sys.path.append("../utils")
sys.path.insert(0,"../../swig")

import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <srcfile1> <srcfile2>"
        sys.exit(1)

    srcfile1 = sys.argv[1]
    srcfile2 = sys.argv[2]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    FIn = snap.TFIn(srcfile1)
    t1 = snap.TTable.Load(FIn, context)
    t.show("load bin", t1)
    r.show("__loadbin__")

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Index", snap.atInt))
    t2 = snap.TTable.LoadSS("2", schema, srcfile2, context, "\t", snap.TBool(False))
    t.show("load text", t2)
    r.show("__loadtext__")

    t3 = t1.Join("Src", t2, "Index")
    t.show("join", t3)
    r.show("__join__")

