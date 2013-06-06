import xml.dom.minidom as xml
import elementtree.ElementTree as ET
import pyutils
import cond
import string
import types as ty
import csv
import os
import copy

class ColumnNotFoundError(Exception):
  def __init__(self, msg = None):
    self.message = "Column not found"
    if not msg is None:
      self.message += ": " + msg
    super(ColumnNotFoundError, self).__init__(self.message)

class Table(object):
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

  def mirror(self,table):
    self.cols = table.cols
    self.types = table.types
    self.data = table.data
    self.dumpcnt = 0

  def initTypes(self):
    """
    Finds type of each column and converts values accordingly
    """
    self.types = [ty.NoneType]*self.numcols()
    for k,row in enumerate(self.data):
      for i in range(self.numcols()):
        val = row[i]
        typ = self.types[i]
        if not val is None:
          if typ in [ty.NoneType,ty.IntType]:
            if val.isdigit():
              row[i] = int(val)
            if val.startswith('-') and val[1:].isdigit():
              row[i] = -int(val[1:])
            self.types[i] = ty.IntType
            continue
          if typ in [ty.NoneType,ty.IntType,ty.FloatType]:
              try:
                row[i] = float(val)
                if not typ == ty.FloatType:
                  self.types[i] = ty.FloatType
                  # Convert already existing values
                  for j in range(k):
                    elt = self.data[j][i]
                    self.data[j][i] = None if elt is None else float(elt)
                continue
              except ValueError:
                pass
          if typ in [ty.NoneType,pyutils.Date]:
            try:
              row[i] = pyutils.Date(val)
              self.types[i] = pyutils.Date
              continue
            except ValueError:
              pass
          row[i] = unicode(val)
          if not typ == ty.UnicodeType:
            self.types[i] = ty.UnicodeType
            # Convert already existing values
            for j in range(k):
              elt = self.data[j][i]
              self.data[j][i] = None if elt is None else unicode(elt)

  def load(self,filename):
    """
    Load data from file. Erases all existing data in the table.
    """
    basename = os.path.basename(filename)
    self.name, ext = os.path.splitext(basename)
    if ext == '.xml':
      self.load_xml(filename)
    elif ext == '.tsv':
      self.load_tsv_fast(filename)
    elif ext == '.tsvs':
      self.load_tsv(filename)
    else:
      print 'Error: only .xml and .tsv files are supported'

  def load_xml(self,filename):
    """
    Load data from XML file. Erases all existing data in the table
    """
    self.initvars()
    source = iter(ET.iterparse(filename, events = ('start','end')))
    self.name = source.next()[1].tag
    for event,elem in source:
      if event == 'end' and elem.tag == 'row':
        row = [None]*self.numcols()
        for name,val in elem.attrib.items():
          try:
            idx = self.getColIndex(name)
          except ColumnNotFoundError:
            idx = len(self.cols)
            row.append(None)
            # Add new column to the table
            self.cols.append(set([name]))
            for oldrow in self.data:
              oldrow.append(None)
          row[idx] = val
        self.data.append(row)
    self.initTypes()

  def load_xml_batch(self,filename):
    self.initvars()
    with open(filename, 'r') as f:
      dom = xml.parse(f)
      self.name = dom.documentElement.tagName
      xmlrows = dom.getElementsByTagName('row')
      for xmlrow in xmlrows:
        row = [None]*self.numcols()
        for name,val in xmlrow.attributes.items():
          try:
           idx = self.getColIndex(name)
          except ColumnNotFoundError:
            idx = len(self.cols)
            row.append(None)
            # Add new column to the table
            self.cols.append(set([name]))
            for oldrow in self.data:
              oldrow.append(None)
          row[idx] = val
        self.data.append(row)
    self.initTypes()

  def load_tsv(self,filename):
    self.initvars()
    with open(filename, 'r') as f:
      data = csv.reader(f,delimiter='\t')
      colnames = data.next()
      self.cols = [set([cell.decode('unicode-escape')]) for cell in colnames]
      for row in data:
        self.data.append([None if val == '' else val.decode('unicode-escape') for val in row])
    self.initTypes()

  def load_tsv_fast(self,filename):
    self.initvars()
    with open(filename, 'r') as f:
      header = f.next()
      self.cols = [set([cell.decode('unicode-escape')]) for cell in header.split('\t')]
      for line in f:
        self.data.append([None if val == '' else val.decode('unicode-escape') for val in line.split('\t')])
    self.initTypes()

  def write_tsv(self, filename):
    """
    Write the data to a TSV file
    """
    f = open(filename,'wb')
    wr = csv.writer(f,delimiter='\t',quoting=csv.QUOTE_ALL)
    colrow = []
    for col in self.cols:
      colrow.append('<undefined>' if len(col) == 0 else unicode(iter(col).next()).encode('unicode-escape'))
    wr.writerow(colrow)
    for row in self.data:
      strrow = []
      for cell in row:
        strrow.append('' if cell is None else unicode(cell).encode('unicode-escape'))
      wr.writerow(strrow)
    f.close()

  def write_tsv_fast(self, filename):
    """
    Write the data to a TSV file without quotation marks
    """
    # TODO (without quotation marks)
    with open(filename, 'wb') as f:
      colnames = ['<undefined>' if len(col) == 0 else unicode(iter(col).next()).encode('unicode-escape') for col in self.cols]
      f.write('\t'.join(colnames)+'\n')
      for row in self.data:
        f.write('\t'.join(['' if cell is None else unicode(cell).encode('unicode-escape') for cell in row])+'\n')

  def dump(self,n=-1,reset=False,*cols):
    """
    Dumps n rows of the table to console.
    If n is not given, the full table is dumped.
    If reset=True, the dump starts over from the 1st row.
    """
    if len(cols) == 0:
      colidx = range(len(self.cols))
    else:
      colidx = self.getColIndexes(cols) 
    if n == -1:
      n = self.numrows()
    if reset:
      self.dumpcnt = 0
    colwidth = 17
    makedumprow = lambda l: '| '+' | '.join(l)+' |\n'
    # Build the header by arranging column labels in rows
    labels = map(list,[self.cols[i] for i in colidx])
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
      dump += makedumprow([string.ljust(unicode(self.data[i][j])[:colwidth],colwidth) for j in colidx])
      self.dumpcnt += 1
    dump += sep
    print dump

  def copy(self):
    t = self.__class__()
    t.cols = copy.deepcopy(self.cols)
    t.types = copy.deepcopy(self.types)
    t.dumpcnt = 0
    for row in self.data:
      t.data.append(row)
    return t

  def getColIndex(self,name):
    idx = 0
    for labels in self.cols:
      if name in labels:
        return idx
      idx += 1
    raise ColumnNotFoundError(name)
  def getColIndexes(self,names):
    return [self.getColIndex(name) for name in names]
  def getLabels(self):
    return set.union(*self.cols)
  def hasLabel(self,name):
    return name in self.getLabels()

  def numcols(self):
    return len(self.cols)
  def numrows(self):
    return len(self.data)

  def label(self,col,label):
    # first remove this label if it's already assigned to a column
    for c in self.cols:
      c.discard(label)
    idx = self.getColIndex(col)
    self.cols[idx].add(label)
    return idx; # Return column index

  def get_selection_val(self, string):
    string = string.strip()
    if string[0] == "\"" and string[-1] == "\"":
      return string[1:-1]
    elif string in cond.OPERATORS:
      return string
    else:
      try:
        return int(string)
      except ValueError:
        try:
          return float(string)
        except ValueError:
          try:
            return cond.Colname(string)
          except ValueError:
            raise ColumnNotFoundError("Couldn't find column \"" + string + "\"")

  def select(self,expr):
    c = cond.Condition(map(self.get_selection_val,expr))
    data = []
    for row in self.data:
      rowdict = self.getRowDict(row)
      if c.eval(rowdict):
        data.append(row)
    self.data = data

  def join(self,col1,table2,col2):
    col1idx = self.getColIndex(col1)
    col2idx = table2.getColIndex(col2)
    if col2idx is None:
      raise ColumnNotFoundError(col2)
    # Compute result of join in a new table
    jointable = Table()
    jointable.cols = self.cols + table2.cols
    jointable.types = self.types + table2.types
    # First remove rows with a None value in either of the two columns:
    self.removeNoneInCol(col1)
    table2.removeNoneInCol(col2)
    # Use dictionary to map the values from table2 to their row index
    table2vals = {}
    for idx,row in enumerate(table2.data):
      val = row[col2idx]
      if not val in table2vals:
        table2vals[val] = []
      table2vals[val].append(idx)
    for row in self.data:
      val = row[col1idx]
      if val in table2vals:
        for idx in table2vals[val]:
          jointable.data.append(row + table2.data[idx])
    # Remove duplicate labels
    addlabels = table2.getLabels()
    for i in range(len(self.cols)):
      jointable.cols[i] = jointable.cols[i].difference(addlabels)
    self.mirror(jointable)

  def removeNoneInCol(self,col):
    colidx = self.getColIndex(col)
    for i in xrange(len(self.data)-1,-1,-1):
      if self.data[i][colidx] is None:
        del self.data[i]

  def getRowDict(self,row):
    rdict = {}
    for i,val in enumerate(row):
      # add key-value for all of the column's labels
      for label in self.cols[i]:
        rdict[label] = val
    return rdict

  def appendOp(self,method,newcolname,*cols):
    # appendOp appends a new column to the table and then calls the specified method
    # (group, order, number or count)
    indexes = self.getColIndexes(cols)
    self.cols.append(set([newcolname]))
    self.types.append(ty.IntType)
    getattr(self,method)(indexes)

  def group(self,indexes):
    tupledict = {}
    groupcnt = 0
    for row in self.data:
      tup = tuple(row[i] for i in indexes)
      if not tup in tupledict:
        groupcnt += 1
        tupledict[tup] = groupcnt
      row.append(tupledict[tup])

  def order(self,indexes):
    tuplelist = [tuple(row[i] for i in indexes) for row in self.data]
    order = [elt[0] for elt in sorted(enumerate(tuplelist), key=lambda x:x[1])]
    for pos,idx in enumerate(order):
      self.data[idx].append(pos+1)

  def number(self,indexes):
    tupledict = {}
    for row in self.data:
      tup = tuple(row[i] for i in indexes)
      if not tup in tupledict:
        tupledict[tup] = 0
      tupledict[tup] += 1
      row.append(tupledict[tup])

  def count(self,indexes):
    tupledict = {}
    for row in self.data:
      tup = tuple(row[i] for i in indexes)
      if not tup in tupledict:
        tupledict[tup] = 0
      tupledict[tup] += 1
    for row in self.data:
      tup = tuple(row[i] for i in indexes)
      row.append(tupledict[tup])

  def next(self,wcol,groupcol,ordercol,valnext):
    wcolidx = self.getColIndex(wcol)
    groupidx = self.getColIndex(groupcol)
    orderidx = self.getColIndex(ordercol)
    self.cols.append(set([valnext]))
    self.types.append(self.types[wcolidx])
    tupledict = {}
    for pos,row in enumerate(self.data):
      group = row[groupidx]
      if not group in tupledict:
        tupledict[group] = []
      tupledict[group].append((pos,row[orderidx],row[wcolidx]))
    for tuples in tupledict.values():
      tuples.sort(key=lambda x: x[1])
      for i in range(len(tuples)-1):
        pos = tuples[i][0]
        nextval = tuples[i+1][2]
        self.data[pos].append(nextval)
      pos = tuples[len(tuples)-1][0]
      self.data[pos].append(None)

  def unique(self,*cols):
    indexes = self.getColIndexes(cols)
    tupleset = set()
    # iterating backwards to remove rows on the fly
    for i in xrange(len(self.data)-1,-1,-1):
      tup = tuple(self.data[i][j] for j in indexes)
      if tup in tupleset:
        del self.data[i]
      else:
        tupleset.add(tup)