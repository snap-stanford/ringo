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
        print """Usage: """ + sys.argv[0] + """ <postsfile> <tagsfile>
        postsfile: posts.tsv file from StackOverflow dataset
        tagsfile: tags.tsv file from StackOverflow dataset"""
        sys.exit(1)

    postsfile = sys.argv[1]
    tagsfile = sys.argv[2]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Id", snap.atInt))
    schema.Add(snap.TStrTAttrPr("OwnerUserId", snap.atInt))
    schema.Add(snap.TStrTAttrPr("AcceptedAnswerId", snap.atInt))
    schema.Add(snap.TStrTAttrPr("CreationDate", snap.atStr))
    schema.Add(snap.TStrTAttrPr("Score", snap.atInt))
    posts = snap.TTable.LoadSS("1", schema, postsfile, context, "\t", snap.TBool(False))
    t.show("load posts text", posts)
    r.show("__loadpoststext__")

    S = snap.Schema()
    S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
    S.Add(snap.TStrTAttrPr("Tag", snap.atStr))
    tags = snap.TTable.LoadSS("2", S, tagsfile, context, '\t', snap.TBool(False))
    t.show("load tags text", tags)
    r.show("__loadtagstext__")

    table = posts.Join("Id", tags, "PostId")
    t.show("join", table)
    r.show("__join__")

    table = table.Join("1.AcceptedAnswerId", posts, "Id")
    t.show("join", table)
    r.show("__join__")

    table.SetSrcCol("1_2.1.AcceptedAnswerId")
    table.SetDstCol("1.Id")
    table = table.ToGraphPerGroup("1_2.2.Tag", snap.aaFirst)
    t.show("graphseq", table)
    r.show("__graphseq__")

