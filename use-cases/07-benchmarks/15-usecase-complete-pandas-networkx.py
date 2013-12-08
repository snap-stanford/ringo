import os
import resource
import sys
import time
import pandas as pd
import networkx as nx
import pdb

sys.path.append("../utils")

import snap
import testutils

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print """Usage: """ + sys.argv[0] + """ <postsfile> <dstfile>
        postsfile: posts.tsv file from StackOverflow dataset
        dstfile: destination file for saving the pagerank table"""
        sys.exit(1)

    def pandas_rename(df,col,name):
      newcolumns = []
      for c in list(df.columns):
        if c == col:
          newcolumns.append(name)
        elif c == name:
          newcolumns.append('<undefined>')
        else:
          newcolumns.append(c)
      df.columns = newcolumns

    postsfile = sys.argv[1]
    dstfile = sys.argv[2]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    posts = pd.read_csv(postsfile, sep='\t', error_bad_lines=False, \
        names=['Id', 'OwnerUserId', 'AcceptedAnswerId', 'CreationDate', 'Score', 'Tag'])
    t.show("load posts text", posts)
    r.show("__loadpoststext__")

    posts1 = posts[posts['Tag'] == 'python']
    t.show("select tag = 'python'", posts1)
    r.show("__selecttagpython__")
    
    posts1 = posts1[posts1['AcceptedAnswerId'] != 0]
    t.show("select question", posts1)
    r.show("__selectquestion__")

    posts2 = posts[posts['AcceptedAnswerId'] == 0]
    t.show("select answer", posts2)
    r.show("__selectanswer__")

    pandas_rename(posts1, "AcceptedAnswerId", "Id")
    qa = pd.merge(posts1, posts2, on='Id')
    t.show("join", qa)
    r.show("__join__")

    qa_proj = qa[['OwnerUserId_x','OwnerUserId_y']]
    graph = nx.from_edgelist(qa_proj.values.tolist())
    t.show("graph", graph)
    r.show("__graph__")

    pr = nx.pagerank(graph, max_iter=100, tol=1e-4)
    pr = pd.DataFrame([[val1, val2] for val1, val2 in pr.items()])
    t.show("pagerank", pr)
    r.show("__pagerank__")

    pr.save(dstfile)
    t.show("save", pr)
    r.show("__save__")
