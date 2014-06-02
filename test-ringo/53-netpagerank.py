import sys
import os
import time

sys.path.append("../utils")
sys.path.append("../ringo-engine-python")
import ringo
import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <graph>"
        sys.exit(1)

    srcfile = sys.argv[1]
    ringo = ringo.Ringo()

    t = testutils.Timer()
    r = testutils.Resource()

    ''' Ringo equivalent ?
    FIn = snap.TFIn(srcfile)
    g = snap.TNEANet.Load(FIn) 
    t.show("load graph", g)
    r.show("__loadbin__")
    '''
