import sys
sys.path.append("../utils")

import snap
import testutils

if __name__ == '__main__':

    srcfile = '/dfs/ilfs2/0/ringo/StackOverflow_joined/debug.tsv'

    context = snap.TTableContext()

    print "Loading table..."
    schema = snap.Schema()
    schema.Add(snap.TStrTAttrPr("Val", snap.atInt))
    table = snap.TTable.LoadSS("1", schema, srcfile, context, "\t", snap.TBool(False))

    print "Selecting rows with val == 0 in place..."
    table.SelectAtomicIntConst("Val", 0, snap.EQ)
    print "Number of rows in result: %d" % table.GetNumValidRows()
    print "10 first rows of table:"
    testutils.dump(table, 10)
