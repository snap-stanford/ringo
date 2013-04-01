import table as tb

class WorkingTableError(Exception):
  def __str__(self):
    return 'Working table not set'
class WorkingColumnError(Exception):
  def __str__(self):
    return 'Working column not set'
class TableNotFoundError(Exception):
  def __init__(self,name):
    self.name = name
  def __str__(self):
    return 'Table not found: ' + str(self.name)
class ColumnNotFoundError(Exception):
  def __init__(self,name):
    self.name = name
  def __str__(self):
    return 'Column not found: ' + str(self.name)

class Ringo:
  """
  Main class - allows the user to import a dataset and create graphs
  """
  def __init__(self):
    self.tables = []
    self.wtable = None # Working table name
    self.wcol = None # Working column label
    self.nodetable = None # Table obtained after applying the node description
                          # to the initial working table

  def load(self,filename):
    t = tb.Table(filename)
    # it would be nicer to check if a table with this name already exists before reading
    # the whole file (requires finding the table name without parsing the full XML document)
    if not t.name in self.tableNames():
      self.tables.append(t)

  # Set working table and working column by name
  def setWorkingTable(self,name):
    self.wtable = self.getTable(name)
  def setWorkingColumn(self,name):
    if self.wtable is None:
      raise WorkingTableError()
    if self.wtable.hasLabel(name):
      self.wcol = name
    else:
      raise ColumnNotFoundError(name)

  def tableNames(self):
    return [t.name for t in self.tables]
  def getTable(self,name):
    for t in self.tables:
      if t.name == name:
        return t
    raise TableNotFoundError(name)

  def dump(self,n=-1,reset=False):
    if self.wtable is None:
      raise WorkingTableError()
    self.wtable.dump(n,reset)

  def label(self,col,label):
    idx = self.wtable.getColIndex(label)
    if not idx is None:
      self.wtable.addLabel(col,label)

  def select(self,expr):
    self.wtable.select(expr)

  def join(self,name,col):
    if self.wtable is None:
      raise WorkingTableError()
    if self.wcol is None:
      raise WorkingColumnError()
    wcolidx = self.wtable.getColIndex(self.wcol)
    table2 = self.getTable(name)
    colidx = table2.getColIndex(col)
    if colidx is None:
      raise ColumnNotFoundError(col)
    # Compute result of join in a new table
    jointable = tb.Table()
    jointable.cols = self.wtable.cols + table2.cols
    jointable.types = self.wtable.types + table2.types
    for row1 in self.wtable.data:
      for row2 in table2.data:
        # Note: if the user attempts to join two columns with incompatible types,
        # the result will be empty
        if row1[wcolidx] == row2[colidx]:
          jointable.data.append(row1 + row2)
    # Remove duplicate labels
    addlabels = table2.labels()
    for i in range(len(self.wtable.cols)):
      jointable.cols[i] = jointable.cols[i].difference(addlabels)
    # Update working table and working column
    self.wcol = col
    self.wtable = jointable