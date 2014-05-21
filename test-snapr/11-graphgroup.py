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
    schema.Add(snap.TStrTAttrPr("CreationDate", snap.atInt))
    schema.Add(snap.TStrTAttrPr("Score", snap.atInt))
    posts = snap.TTable.LoadSS(schema, postsfile, context, "\t", snap.TBool(False))
    t.show("load posts text", posts)
    r.show("__loadpoststext__")

    S = snap.Schema()
    S.Add(snap.TStrTAttrPr("PostId", snap.atInt))
    S.Add(snap.TStrTAttrPr("Tag", snap.atStr))
    tags = snap.TTable.LoadSS(S, tagsfile, context, '\t', snap.TBool(False))
    t.show("load tags text", tags)
    r.show("__loadtagstext__")

    table = posts.Join("Id", tags, "PostId")
    t.show("join", table)
    r.show("__join__")

    table = table.Join("AcceptedAnswerId", posts, "Id")
    t.show("join", table)
    r.show("__join__")

    table.SetSrcCol("OwnerUserId-1")
    table.SetDstCol("OwnerUserId-2")
    gseq = table.ToGraphPerGroup("Tag", snap.aaFirst)
    t.show("graphseq", gseq)
    r.show("__graphseq__")

