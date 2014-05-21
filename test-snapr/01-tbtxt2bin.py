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

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <srcfile> <dstfile>"
        sys.exit(1)

    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Src", snap.atInt))
    schema.Add(snap.TStrTAttrPr("Dst", snap.atInt))
    table = snap.TTable.LoadSS(schema, srcfile, context, "\t", snap.TBool(False))
    t.show("load text", table)
    r.show("__loadtext__")

    FOut = snap.TFOut(dstfile)
    table.Save(FOut)
    t.show("save bin", table)
    r.show("__savebin__")

