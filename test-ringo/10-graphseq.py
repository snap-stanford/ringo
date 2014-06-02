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

WINDOW_SIZE = 2592000 # 1 month

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print """Usage: """ + sys.argv[0] + """ <srcfile>
        srcfile: posts.tsv file from StackOverflow dataset"""
        sys.exit(1)

    srcfile = sys.argv[1]
    ringo = ringo.Ringo()
  
    t = testutils.Timer()
    r = testutils.Resource()

    S = [("Id", "int"), ("OwnerUserId", "int"), ("AcceptedAnswerId", "int"), ("CreationDate", "string"), ("Score", "int")]
    table = ringo.LoadTableTSV(S, srcfile)
    t.show("load text")
    r.show("__loadtext__")

    table2 = ringo.Join(table, table, "AcceptedAnswerId", "Id")
    t.show("join")
    r.show("__join__")

    gseq = table2.ToGraphSequence("CreationDate-1", snap.aaFirst, WINDOW_SIZE, WINDOW_SIZE)
    t.show("graphseq", gseq)
    r.show("__graphseq__")
