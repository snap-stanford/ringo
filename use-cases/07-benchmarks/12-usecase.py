import os
import resource
import sys
import time
import pdb

sys.path.append("../utils")

import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print """Usage: """ + sys.argv[0] + """ <srcfile> <dstfile>
        postsfile: posts.tsv file from StackOverflow dataset
        dstfile: destination file for saving the pagerank table"""
        sys.exit(1)

    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
    schema.Add(snap.TStrTAttrPr("OwnerUserId", snap.atInt))
    schema.Add(snap.TStrTAttrPr("AcceptedAnswerId", snap.atInt))
    schema.Add(snap.TStrTAttrPr("CreationDate", snap.atInt))
    schema.Add(snap.TStrTAttrPr("Score", snap.atInt))
    schema.Add(snap.TStrTAttrPr("Tag", snap.atStr))
    table = snap.TTable.LoadSS("1", schema, srcfile, context, "\t", snap.TBool(False))
    t.show("load posts text", table)
    r.show("__loadpoststext__")

    questions = snap.TTable.New("2", table.GetSchema(), context)
    table.SelectAtomicStrConst("Tag", "python", snap.EQ, questions)
    t.show("selected tag = 'python'", questions)
    r.show("__selectedtagpython__")

    qa = questions.Join("AcceptedAnswerId", table, "Id")
    t.show("join", qa)
    r.show("__join__")

    qa.SetSrcCol("2.OwnerUserId")
    qa.SetDstCol("1.OwnerUserId")
    graph = qa.ToGraph(snap.aaFirst)
    t.show("graph", graph)
    r.show("__graph__")

    PRankH = snap.TIntFltH()
    snap.GetPageRank(graph, PRankH,  0.85, 1e-4, 100)
    prtable = snap.TTable.New("PR", PRankH, "UserId", "PageRank", context, snap.TBool(True))
    t.show("pagerank", prtable)
    r.show("__pagerank__")

    FOut = snap.TFOut(dstfile)
    prtable.Save(FOut)
    t.show("save bin", prtable)
    r.show("__savebin__")
