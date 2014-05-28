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
    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <srcfile1> <srcfile2>"
        sys.exit(1)
    srcfile1 = sys.argv[1]
    srcfile2 = sys.argv[2]
  
    ringo = ringo.Ringo()

    t = testutils.Timer()
    r = testutils.Resource()

    t1 = ringo.LoadTableBinary(srcfile1)
    t.show("load bin")
    r.show("__loadbin__")

    S = [("Index", "int")]
    t2 = ringo.LoadTableTSV(S, srcfile2)
    t.show("load text")
    r.show("__loadtext__")

    t3 = ringo.Join(t1, t2, "Src", "Index")
    t.show("join")
    r.show("__join__")
