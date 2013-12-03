"""
 Use case #2: create a coauthorship network and get the table of authors sorted by PageRank score
"""

import sys
sys.path.append("..")
import os
import time
import snap
import testutils

N_TOP_AUTHORS = 20
ENABLE_TIMER = True
OUTPUT_TABLE_FILENAME = "table.tsv"
PAGE_RANK_ATTRIBUTE = "PageRank"
NODE_ATTR_NAME = "__node_attr"

if len(sys.argv) < 2:
  print """Usage: python 02-DBLP-snap.py <authors.tsv> <year.tsv> <outputdir>
  authors.tsv: path to authors.tsv file
  year.tsv: path to year.tsv file
  outputdir: output directory"""
  exit(1)
authorFile = sys.argv[1]
yearFile = sys.argv[2]
dstDir = sys.argv[3] if len(sys.argv) >= 4 else None
if not dstDir is None:
  try:
    os.makedirs(dstDir)
  except OSError:
    pass

context = snap.TTableContext()

t = testutils.Timer(ENABLE_TIMER)

# Load data
# >>> authors = ringo.load('authors.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("Key", snap.atStr))
S.Add(snap.TStrTAttrPr("Author", snap.atStr))
authors = snap.TTable.LoadSS("1", S, authorFile, context, '\t', snap.TBool(False))
t.show("load authors table", authors)

# >>> year = ringo.load('year.tsv')
S = snap.Schema()
S.Add(snap.TStrTAttrPr("Key", snap.atStr))
S.Add(snap.TStrTAttrPr("Year", snap.atInt))
year = snap.TTable.LoadSS("2", S, yearFile, context, '\t', snap.TBool(False))
t.show("load year table", year)

# Select
# >>> year.select('Year >= 2005')
year.SelectAtomicIntConst("Year", 2005, snap.GTE)
t.show("select", year)

# Join
# >>> table = authors.join(year, ['Key'], ['Key'])
table = authors.Join("Key", year, "Key")
t.show("join", table)

# Self-join
# >>> table.selfjoin(table, ['Key'])
table = table.SelfJoin("Key")
t.show("join", table)

# Select
# >>> table.select('Author_1 != Author_2')
table.SelectAtomic("1_2_1.1.Author", "1_2_2.1.Author", snap.NEQ)
t.show("select", table)

# Create network
# >>> table.graph('Author_1', 'Author_2', directed=False)
table.SetSrcCol("1_2_1.1.Author")
table.SetDstCol("1_2_2.1.Author")
graph = table.ToGraph(snap.aaFirst)
t.show("graph", graph)

# Compute PageRank score
# >>> pagerank = graph.pageRank('PageRank')
HT = snap.TIntFltH()
snap.GetPageRank(graph, HT)
pagerank = snap.TTable.New("PR", HT, "Author", PAGE_RANK_ATTRIBUTE, context, snap.TBool(True))
t.show("page rank", pagerank)

# Order by PageRank score (in descending order)
# >>> pagerank.order(['PageRank'], desc = True)
V = snap.TStrV()
V.Add(PAGE_RANK_ATTRIBUTE)
pagerank.Order(V, "", snap.TBool(False), snap.TBool(False))
t.show("order", pagerank)

# Normalize PageRank scores so that the top score is 1
# >>> topPageRank = pagerank.first()['PageRank']
# >>> pagerank.arith('PageRank / {0}'.format(topPageRank))
topPageRank = pagerank.BegRI().GetFltAttr("PageRank")
pagerank.ColDiv("PageRank", topPageRank)
t.show("division", pagerank)

# Save final table
# >>> pagerank.save('table.tsv')
if not dstDir is None:
  pagerank.SaveSS(os.path.join(dstDir,OUTPUT_TABLE_FILENAME))
  t.show("save", pagerank)

# Print top authors with their PageRank score
testutils.dump(pagerank, N_TOP_AUTHORS)
