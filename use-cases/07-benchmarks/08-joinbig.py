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
    t1 = snap.TTable.Load(FIn, context)
    t.show("load bin", t1)
    r.show("__loadbin__")

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Index", snap.atInt))
    t2 = snap.TTable.New(snap.TStr("2"), schema, context)
    IntVals = snap.TIntV()
    FltVals = snap.TFltV()
    StrVals = snap.TStrV()
    for i in range(4837570):
        IntVals.Clr()
        IntVals.Add(i)
        t2.AddRow(IntVals, FltVals, StrVals)
    t2.InitIds()
    t.show("created table with vals 0..4837570", t2)
    r.show("__createdtablewithvals4837570__")

    t3 = t1.Join("Src", t2, "Index")
    t.show("joined t1 and t2 on first columns", t3)
    r.show("__joinedt1t2firstcols__")
