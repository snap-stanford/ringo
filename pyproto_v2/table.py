import xml.dom.minidom as xml
import utils
import cond
import string
import types as ty

class Table:
  """
  Used to load and transform tables
  """
  def __init__(self,filename=None):
    self.initvars()
    if not filename is None:
      self.load(filename)

  def initvars(self):
    self.cols = [] # list of columns - each column is represented by a set of labels
    self.types = [] # contains type of each column (int,float,date or string)
    self.data = [] # list of rows
    self.dumpcnt = 0

  def load(self,filename):
    """
    Load data from XML file. Erases all existing data in the table
    """
    self.initvars()
    with open(filename, 'r') as f:
      dom = xml.parse(f)
      self.name = dom.documentElement.tagName
      xmlrows = dom.getElementsByTagName('row')
      for xmlrow in xmlrows:
        row = [None]*self.numcols()
        for name,val in xmlrow.attributes.items():
          idx = self.getColIndex(name)
          if idx is None:
            idx = len(self.cols)
            row.append(None)
            # Add new column to the table
            self.cols.append(set([name]))
            for oldrow in self.data:
              oldrow.append(None)
          row[idx] = val
        self.data.append(row)
    # Find type of each column and convert values accordingly
    self.types = [ty.NoneType]*self.numcols()
    for row in self.data:
      for i in range(self.numcols()):
        val = row[i]
        typ = self.types[i]
        if not val is None:
          if typ in [ty.NoneType,ty.IntType] and val.isdigit():
            row[i] = int(val)
            self.types[i] = ty.IntType
            continue
          if typ in [ty.NoneType,ty.IntType,ty.FloatType]:
              try:
                row[i] = float(val)
                self.types[i] = ty.FloatType
                continue
              except ValueError:
                pass
          if typ in [ty.NoneType,utils.Date]:
            try:
              row[i] = utils.Date(val)
              self.types[i] = utils.Date
              continue
            except ValueError:
              pass
          self.types[i] = ty.UnicodeType

  def dump(self,n=-1,reset=False):
    """
    Dumps n rows of the table to console.
    If n is not given, the full table is dumped.
    If reset=True, the dump starts over from the 1st row.
    """
    if n == -1:
      n = self.numRows()
    if reset:
      self.dumpcnt = 0
    colwidth = 17
    makedumprow = lambda l: '| '+' | '.join(l)+' |\n'
    # Build the header by arranging column labels in rows
    labels = map(list,self.cols)
    maxnumlabels = max(map(len,labels))
    labels = [l+['']*(maxnumlabels-len(l)) for l in labels]
    labelrows = zip(*labels)
    headerrows = map(makedumprow,[[string.center(label[:colwidth],colwidth) for label in lr] for lr in labelrows])
    dump = ''.join(headerrows)
    sep = '+'*(len(headerrows[0])-1)+'\n'
    dump = sep + dump + sep
    # Dump appropriate number of rows
    for i in [x+self.dumpcnt for x in range(n)]:
      if i >= len(self.data):
        break
      dump += makedumprow([string.ljust(str(val)[:colwidth],colwidth) for val in self.data[i]])
      self.dumpcnt += 1
    dump += sep
    print dump

  def getColIndex(self,name):
    idx = 0
    for labels in self.cols:
      if name in labels:
        return idx
      idx += 1
  def labels(self):
    return set.union(*self.cols)
  def hasLabel(self,name):
    return name in self.labels()

  def numcols(self):
    return len(self.cols)
  def numrows(self):
    return len(self.data)

  def addLabel(self,col,label):
    # first remove this label if it's already assigned to a column
    for c in self.cols:
      c.discard(label)
    idx = self.getColIndex(col)
    if not idx is None:
      self.cols[idx].add(label)

  def select(self,expr):
    c = cond.Condition(expr)
    # iterating backwards to remove rows on the fly
    for i in xrange(len(self.data)-1,-1,-1):
      rowdict = self.getRowDict(self.data[i])
      if not c.eval(rowdict):
        del self.data[i]

  def getRowDict(self,row):
    rdict = {}
    for i,val in enumerate(row):
      # add key-value for all of the column's labels
      for label in self.cols[i]:
        rdict[label] = val
    return rdict