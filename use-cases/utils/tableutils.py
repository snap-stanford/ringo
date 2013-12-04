import snap
import pdb

def addRow(table, values):
  row = snap.TTableRow()
  for val in values:
    if isinstance(val, (int, long)):
      row.AddInt(val)
    elif isinstance(val, float):
      row.AddFlt(val)
    else:
      row.AddStr(val)
  table.AddRow(row)
