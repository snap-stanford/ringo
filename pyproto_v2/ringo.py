import table as tb
import graph as gr
import copy
import time
import inspect
import string
import pdb

class WorkingTableError(Exception):
  def __str__(self):
    return 'Working table not set'
class WorkingColumnError(Exception):
  def __str__(self):
    return 'Working column not set'
#class SourceTableError(Exception):
#  def __str__(self):
#    return 'Source table not set'
#class SourceColumnError(Exception):
#  def __str__(self):
#    return 'Source column not set'
class SourceError(Exception):
  def __str__(self):
    return "Source not set"
class TableNotFoundError(Exception):
  def __init__(self,name):
    self.name = name
  def __str__(self):
    return 'Table not found: ' + str(self.name)
class ReservedNameError(Exception):
  def __str__(self,name):
    return str(self.name) + ' is a reserved name'
class GraphNotDefinedError(Exception):
  def __str__(self):
    return 'Graph not defined'

class Ringo(object):
  SRC_COL_LABEL = '__srccol'
  DEBUG = True

  """
  Main class - allows the user to import a dataset and create graphs
  """
  def __init__(self):
    self.tables = []
    self.wtable = None # Working table name
    self.wcol = None # Working column label
    #self.srctable = None # Table obtained after applying the node description
                          # to the initial working table
    self.graph = None # Output graph

  ####### API FUNCTIONS #######

  def load(self,*filenames):
    start = time.clock()
    for f in filenames:
      t = tb.Table(f)
      # it would be nicer to check if a table with this name already exists before reading
      # the whole file (requires finding the table name without parsing the full XML document)
      if not t.name in self.tableNames():
        self.tables.append(t)
    if self.DEBUG:
      self.showtime(start)

  def start(self,table,col):
    start = time.clock()
    self.setWorkingTable(table)
    self.setWorkingColumn(col)
    if self.DEBUG:
      self.showtime(start)

  def label(self,label):
    start = time.clock()
    if label == self.SRC_COL_LABEL:
      raise ReservedNameError(self.SRC_COL_LABEL)
    self.checkwcontext()
    self.wtable.addLabel(self.wcol,label)
    if self.DEBUG:
      self.showtime(start)

  def select(self,expr):
    start = time.clock()
    self.wtable.select(expr)
    if self.DEBUG:
      self.showtime(start)

  def join_slow(self,tname,col):
    start = time.clock()
    self.dist(tname,col,'eucl',0)
    if self.DEBUG:
      self.showtime(start)

  def join(self,tname,col):
    start = time.clock()
    # TODO: This could be moved into table.py
    self.checkwcontext()
    wcolidx = self.wtable.getColIndex(self.wcol)
    table2 = self.getTable(tname)
    colidx = table2.getColIndex(col)
    if colidx is None:
      raise tb.ColumnNotFoundError(col)
    # Compute result of join in a new table
    jointable = tb.Table()
    jointable.cols = self.wtable.cols + table2.cols
    jointable.types = self.wtable.types + table2.types
    # First remove rows with a None value in either of the two columns:
    self.wtable.removeNoneInCol(self.wcol)
    table2.removeNoneInCol(col)
    # Use dictionary to map the values from table2 to their row index
    table2vals = {}
    for idx,row in enumerate(table2.data):
      val = row[colidx]
      if not val in table2vals:
        table2vals[val] = []
      table2vals[val].append(idx)
    for row in self.wtable.data:
      val = row[wcolidx]
      if val in table2vals:
        for idx in table2vals[val]:
          jointable.data.append(row + table2.data[idx])
    # Remove duplicate labels
    addlabels = table2.labels()
    for i in range(len(self.wtable.cols)):
      jointable.cols[i] = jointable.cols[i].difference(addlabels)
    # Update working table and working column
    self.wcol = col
    self.wtable = jointable
    if self.DEBUG:
      self.showtime(start)

  def dist(self,tname,col,metric,threshold):
    # TODO: This could be moved into table.py
    self.checkwcontext()
    wcolidx = self.wtable.getColIndex(self.wcol)
    table2 = self.getTable(tname)
    colidx = table2.getColIndex(col)
    if colidx is None:
      raise tb.ColumnNotFoundError(col)
    # Compute result of join in a new table
    outputTable = tb.Table()
    outputTable.cols = self.wtable.cols + table2.cols
    outputTable.types = self.wtable.types + table2.types
    distMethod = getattr(self,metric)
    # First remove rows with a None value in either of the two columns:
    self.wtable.removeNoneInCol(self.wcol)
    table2.removeNoneInCol(col)
    # Use double loop to compare all pairs (slow!)
    for row1 in self.wtable.data:
      for row2 in table2.data:
        # Note: if the user attempts to compare two columns with incompatible types,
        # the result will be empty
        if distMethod(row1[wcolidx],row2[colidx]) <= threshold:
          outputTable.data.append(row1 + row2)
    # Remove duplicate labels
    addlabels = table2.labels()
    for i in range(len(self.wtable.cols)):
      outputTable.cols[i] = outputTable.cols[i].difference(addlabels)
    # Update working table and working column
    self.wcol = col
    self.wtable = outputTable

  def callAppendOp(self,method,newcolname,*cols):
    self.checkwtable()
    if len(cols) == 0:
      self.checkwcol()
      cols = [self.wcol]
    self.wtable.appendOp(method,newcolname,*cols)
    self.setWorkingColumn(newcolname)

  def group(self,newcolname,*cols):
    start = time.clock()
    self.callAppendOp("group",newcolname,*cols)
    if self.DEBUG:
      self.showtime(start)

  def order(self,newcolname,*cols):
    start = time.clock()
    self.callAppendOp("order",newcolname,*cols)
    if self.DEBUG:
      self.showtime(start)

  def number(self,newcolname,*cols):
    start = time.clock()
    self.callAppendOp("number",newcolname,*cols)
    if self.DEBUG:
      self.showtime(start)

  def count(self,newcolname,*cols):
    start = time.clock()
    self.callAppendOp("count",newcolname,*cols)
    if self.DEBUG:
      self.showtime(start)

  def next(self,groupcol,ordercol,valnext):
    start = time.clock()
    self.checkwcontext()
    self.wtable.next(self.wcol,groupcol,ordercol,valnext)
    self.setWorkingColumn(valnext)
    if self.DEBUG:
      self.showtime(start)

  def unique(self):
    start = time.clock()
    self.checkwcontext()
    self.wtable.unique(self.wcol)
    if self.DEBUG:
      self.showtime(start)

  def link(self,name):
    start = time.clock()
    self.setWorkingColumn(name)
    if self.DEBUG:
      self.showtime(start)

  #def makegraph(self,gtype='directed',nodeattr=[],edgeattr=[],destnodeattr=[]):
  def makegraph(self,gtype='directed',edgeattr=[]):
    start = time.clock()
    self.checksource()
    self.checkwcontext()
    srcidx = self.wtable.getColIndex(self.SRC_COL_LABEL)
    destidx = self.wtable.getColIndex(self.wcol)
    edgeattridx = self.wtable.getColIndexes(edgeattr)
    #destattridx = self.wtable.getColIndexes(destnodeattr)
    self.graph.setType(gtype)
    for row in self.wtable.data:
      srcnode = row[srcidx]
      destnode = row[destidx]
      # If the destination node doesn't exist yet, it is added to the graph (without attributes)
      self.graph.addedge(srcnode,destnode,[row[i] for i in edgeattridx])
    if self.DEBUG:
      self.showtime(start)

  ##### METRICS (DISTANCE-BASED GRAPHS) ######
  def eucl(self,val1,val2):
    return abs(val1-val2)

  ##### UTILITY FUNCTIONS #####

  # Pretty printing for the working table and the graph
  def tdump(self,n=-1,reset=False,*cols):
    self.checkwtable()
    self.wtable.dump(n,reset,*cols)
  def gdump(self,n=-1,reset=False):
    if self.graph is None:
      raise GraphNotDefinedError()
    self.graph.dump(n,reset)
  def dump(self,ntable=-1,ngraph=-1,reset=True):
    self.tdump(ntable,reset,self.SRC_COL_LABEL,self.wcol)
    self.gdump(ngraph,reset)

  def setWorkingTable(self,name):
    #self.wtable = copy.deepcopy(self.getTable(name))
    self.wtable = self.getTable(name).copy()
  def setWorkingColumn(self,name):
    self.checkwtable()
    if self.wtable.hasLabel(name):
      self.wcol = name
      self.wtable.removeNoneInCol(self.wcol)  # Remove rows with "None" value
    else:
      raise tb.ColumnNotFoundError(name)
  def setSource(self,attributes=[]):
    start = time.clock()
    self.checkwcontext()
    srcidx = self.wtable.addLabel(self.wcol,self.SRC_COL_LABEL)
    # self.srctable = copy.deepcopy(self.wtable) # This allows to use the current working table again in the future
    # Add source nodes to graph
    self.graph = gr.Graph()
    attridx = self.wtable.getColIndexes(attributes)
    for row in self.wtable.data:
      self.graph.addnode(row[srcidx],[row[i] for i in attridx])
    if self.DEBUG:
      self.showtime(start)
  def tableNames(self):
    return [t.name for t in self.tables]
  def getTable(self,name):
    for t in self.tables:
      if t.name == name:
        return t
    raise TableNotFoundError(name)
  def checkwtable(self):
    if self.wtable is None:
      raise WorkingTableError()
  def checkwcol(self):
    if self.wcol is None:
      raise WorkingColumnError()
  def checkwcontext(self):
    self.checkwtable()
    self.checkwcol()
  def checksource(self):
    self.checkwtable()
    if not self.wtable.hasLabel(self.SRC_COL_LABEL):
      raise SourceError()
  def showtime(self,start):
    method = str(inspect.stack()[1][3])
    message = string.ljust(method,10) + ': ' + str(time.clock() - start) + ' seconds'
    if not self.wtable is None:
      message += ' (' + str(self.wtable.numrows()) + ' rows in working table)'
    print message

