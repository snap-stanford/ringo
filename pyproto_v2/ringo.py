import table as tb
import graph as gr
import copy

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

class Ringo:
  SRC_COL_LABEL = '__srccol'

  """
  Main class - allows the user to import a dataset and create graphs
  """
  def __init__(self):
    self.tables = []
    self.wtable = None # Working table name
    self.wcol = None # Working column label
    self.srctable = None # Table obtained after applying the node description
                          # to the initial working table
    self.graph = None # Output graph

  ####### API FUNCTIONS #######

  def load(self,*filenames):
    for f in filenames:
      t = tb.Table(f)
      # it would be nicer to check if a table with this name already exists before reading
      # the whole file (requires finding the table name without parsing the full XML document)
      if not t.name in self.tableNames():
        self.tables.append(t)

  def label(self,label):
    if label == self.SRC_COL_LABEL:
      raise ReservedNameError(self.SRC_COL_LABEL)
    self.checkwcontext()
    self.wtable.addLabel(self.wcol,label)

  def select(self,expr):
    self.wtable.select(expr)

  def join(self,tname,col):
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

  def callAppendOp(self,method,newcolname,*cols):
    self.checkwtable()
    if len(cols) == 0:
      self.checkwcol()
      cols = [self.wcol]
    self.wtable.appendOp(method,newcolname,*cols)
    self.setWorkingColumn(newcolname)

  def group(self,newcolname,*cols):
    self.callAppendOp("group",newcolname,*cols)

  def order(self,newcolname,*cols):
    self.callAppendOp("order",newcolname,*cols)

  def number(self,newcolname,*cols):
    self.callAppendOp("number",newcolname,*cols)

  def count(self,newcolname,*cols):
    self.callAppendOp("count",newcolname,*cols)

  def next(self,groupcol,ordercol,valnext):
    self.checkwcontext()
    self.wtable.next(self.wcol,groupcol,ordercol,valnext)
    self.setWorkingColumn(valnext)

  def unique(self):
    self.checkwcontext()
    self.wtable.unique(self.wcol)

  def link(self,name):
    self.setWorkingColumn(name)

  #def makegraph(self,gtype='directed',nodeattr=[],edgeattr=[],destnodeattr=[]):
  def makegraph(self,gtype='directed',nodeattr=[],edgeattr=[]):
    self.checkwcontext()
    #self.checksrccontext()
    self.checksource()
    self.graph = gr.Graph(gtype)
    srcidx = self.wtable.getColIndex(self.SRC_COL_LABEL)
    destidx = self.wtable.getColIndex(self.wcol)
    nodeattridx = self.wtable.getColIndexes(nodeattr)
    edgeattridx = self.wtable.getColIndexes(edgeattr)
    #destattridx = self.wtable.getColIndexes(destnodeattr)
    for row in self.wtable.data:
      srcnode = row[srcidx]
      destnode = row[destidx]
      self.graph.addnode(srcnode,[row[i] for i in nodeattridx])
      #self.graph.addnode(destnode,[row[i] for i in destattridx])
      self.graph.addnode(destnode) # If destnode does not yet exist in the graph, the node
                                   # is created without attributes. If destnode also exists
                                   # in the source column, then the attributes will be updated.
      self.graph.addedge(srcnode,destnode,[row[i] for i in edgeattridx])

  ##### UTILITY FUNCTIONS #####

  # Pretty printing for the working table and the graph
  def tdump(self,n=-1,reset=False,*cols):
    self.checkwtable()
    self.wtable.dump(n,reset,*cols)
  def gdump(self,n=-1,reset=False):
    if self.graph is None:
      raise GraphNotDefinedError()
    self.graph.dump(n,reset)
  def dump(self):
    self.tdump(-1,True,self.SRC_COL_LABEL,self.wcol)
    self.gdump(-1,True)

  def setWorkingTable(self,name):
    self.wtable = copy.deepcopy(self.getTable(name))
  def setWorkingColumn(self,name):
    self.checkwtable()
    if self.wtable.hasLabel(name):
      self.wcol = name
    else:
      raise tb.ColumnNotFoundError(name)
  #def setSourceContext(self):
  #  self.checkwcontext()
  #  self.wtable.addLabel(self.wcol,self.SRC_COL_LABEL)
  #  self.srctable = copy.deepcopy(self.wtable)
  def setSource(self,table,col):
    self.setWorkingTable(table)
    self.setWorkingColumn(col)
    self.wtable.addLabel(self.wcol,self.SRC_COL_LABEL)
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

