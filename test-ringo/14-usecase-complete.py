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
        print """Usage: """ + sys.argv[0] + """ <srcfile> <dstfile>
        postsfile: posts.tsv file from StackOverflow dataset
        dstfile: destination file for saving the pagerank table"""
        sys.exit(1)

    srcfile = sys.argv[1]
    dstfile = sys.argv[2]

    ringo = ringo.Ringo()

    t = testutils.Timer()
    r = testutils.Resource()

    S = [("Id", "int"), ("OwnerUserId", "int"), ("AcceptedAnswerId", "int"), ("CreationDate", "string"), ("Score", "int"), ("Tag", "string")]
    table = ringo.LoadTableTSV(S, srcfile)
    t.show("load posts text")
    r.show("__loadpoststext__")

    questions = ringo.Select(table, "Tag = python", False)
    t.show("selected tag = 'python'")
    r.show("__selectedtagpython__")

    ringo.Select(questions, "AcceptedAnswerId != 0")
    t.show("select questions")
    r.show("__selectquestions__")

    ringo.Select(table, "AcceptedAnswerId = 0")
    t.show("select answers")
    r.show("__selectanswers__")

    ringo.Join(questions, table, "AcceptedAnswerId", "Id")
    t.show("join")
    r.show("__join__")

    graph = ringo.ToGraph(qa, "OwnerUserId-2", "OwnerUserId-1")
    t.show("graph")
    r.show("__graph__")

    prtable = ringo.PageRank(graph, 'PageRank', False, 0.85, 1e-4, 100)
    t.show("pagerank")
    r.show("__pagerank__")

    ringo.SaveTableBinary(prtable)
    t.show("save bin")
    r.show("__savebin__")
