import os
import resource
import sys
import time

sys.path.append("../utils")
sys.path.append("../ringo-engine-python")
import ringo
import snap
import testutils

#def Save(self,*args):
    #self().Save(*args)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <srcfile> <dstfile>"
        sys.exit(1)
    ringo = ringo.Ringo()
    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    t = testutils.Timer()
    r = testutils.Resource()

    S = [("Src", "int"), ("Dst", "int")]
    table = ringo.LoadTableTSV(S, srcfile)

    t.show("load text")
    r.show("__loadtext__")

    ringo.Save(table, dstfile)
    t.show("save bin")
    r.show("__savebin__")

    table.GenerateProvenance('provenance_scripts/01.py')
