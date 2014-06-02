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
    if len(sys.argv) < 2:
        print """Usage: """ + sys.argv[0] + """ <postsfile> <tagsfile>
        postsfile: posts.tsv file from StackOverflow dataset
        tagsfile: tags.tsv file from StackOverflow dataset"""
        sys.exit(1)

    postsfile = sys.argv[1]
    tagsfile = sys.argv[2]

    ringo = ringo.Ringo()
    t = testutils.Timer()
    r = testutils.Resource()

    S = [("Id", "int"), ("OwnerUserId", "int"), ("AcceptedAnswerId", "int"), ("CreationDate", "string"), ("Score", "int")]
    posts = ringo.LoadTableTSV(S, postsfile)
    t.show("load posts text")
    r.show("__loadpoststext__")

    S = [("PostId", "int"), ("Tag", "string")]
    tags = ringo.LoadTableTSV(S, tagsfile)
    t.show("load tags text")
    r.show("__loadtagstext__")

    table = ringo.Join(posts, tags, "Id", "PostId")
    t.show("join")
    r.show("__join__")

    table2 = ringo.Join(table, posts, "AcceptedAnswerId", "Id")
    t.show("join")
    r.show("__join__")
    
    gseq = table2.ToGraphPerGroup("Tag", snap.aaFirst)
    t.show("graphseq", gseq)
    r.show("__graphseq__")
