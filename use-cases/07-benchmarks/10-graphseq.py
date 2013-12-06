import os
import resource
import sys
import time
import pdb

sys.path.append("../utils")

import snap
import testutils

WINDOW_SIZE = 2592000 # 1 month

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print """Usage: """ + sys.argv[0] + """ <srcfile>
        srcfile: posts.tsv file from StackOverflow dataset"""
        sys.exit(1)

    srcfile = sys.argv[1]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
    schema.Add(snap.TStrTAttrPr("OwnerUserId", snap.atInt))
    schema.Add(snap.TStrTAttrPr("AcceptedAnswerId", snap.atInt))
    schema.Add(snap.TStrTAttrPr("CreationDate", snap.atStr))
    schema.Add(snap.TStrTAttrPr("Score", snap.atInt))
    table = snap.TTable.LoadSS("1", schema, srcfile, context, "\t", snap.TBool(False))
    t.show("load text", table)
    r.show("__loadtext__")

    table = table.Join("AcceptedAnswerId", table, "Id")
    t.show("join", table)
    r.show("__join__")

    pdb.set_trace()
    table.SetSrcCol("1_1.OwnerUserId")
    table.SetDstCol("1_2.OwnerUserId")
    gseq = table.ToGraphSequence("1_1.CreationDate", snap.aaFirst, WINDOW_SIZE, WINDOW_SIZE)
    t.show("graphseq", gseq)
    r.show("__graphseq__")

