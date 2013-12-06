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

    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + "<srcfile>"
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

    srcfile = sys.argv[1]

    context = snap.TTableContext()

    t = testutils.Timer()
    r = testutils.Resource()

    table = pd.read_csv(srcfile, sep='\t', error_bad_lines=False, names=['Src', 'Dst'])
    t.show("load posts text", table)
    r.show("__loadpoststext__")

    table2 = table[table['Src'] < 10000]
    t.show("selected < 10K new table", table2)
    r.show("__selectedlt10Knewtable__")
