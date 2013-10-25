import graph_engine as ge
import sys, os
import utils
import pdb
sys.path.append(os.path.join(os.path.dirname(__file__), "python_engine"))
import table as tb
import graph as gr

WTABLE_NAME = "wtable"
SRCCOL_NAME = "source"

class InvalidInstructionException(Exception):
  def __init__(self, msg = None):
    self.message = "Invalid instruction"
    if not msg is None:
      self.message += ": " + msg
    super(InvalidInstructionException, self).__init__(self.message)

class PythonGraphEngine(ge.GraphEngine):
  """
  Graph creation engine based on the PYTHON implementation
  """
  def __init__(self):
    self.tables = {}
    self.wtable = None
    self.reset()

  def __uniquify(self):
    """Calls unique() if the flag IS_MULTIGRAPH is not present"""
    if self.src_col is None or self.dst_col is None:
      return
    if self.uniquified == False:
      if not self.is_multigraph:
        # Keep at most one edge between any two nodes
        self.wtable.unique(self.src_col, self.dst_col)
      self.uniquified = True

  def reset(self):
    self.is_multigraph = False
    self.bipartite = False
    self.directed = False
    self.uniquified = False
    self.src_col = None
    self.dst_col = None

  def load(self, filename, tablename = None):
    if tablename is None:
      tablename = utils.get_name_for_table(filename)
    # If a table with the same name already exists, it is overwritten
    self.tables[tablename] = tb.Table(filename)

  def start(self, tablename):
    if not tablename in self.tables:
      raise InvalidInstructionException("Couldn't find table \"" + tablename + "\"")
    self.wtable = self.tables[tablename].copy()
    if self.src_col is None:
      raise InvalidInstructionException('Incomplete query')
    safe_srccol_name = '__' + SRCCOL_NAME
    self.wtable.label(self.src_col, safe_srccol_name)
    self.src_col = safe_srccol_name

  def label(self, column, name):
    self.wtable.label(column, name)
    #self.rename(self.wtable, old_name, new_name)

  def join(self, col1, tablename, col2):
    if not tablename in self.tables:
      raise InvalidInstructionException("Couldn't find table \"" + tablename + "\"")
    self.wtable.join(col1, self.tables[tablename], col2)

  def select(self, *tree):
    self.__uniquify()
    self.wtable.select(tree)

  def count(self, result_col, *cols):
    self.__uniquify()
    self.wtable.appendOp("count",result_col,*cols)

  def group(self, result_col, *cols):
    self.__uniquify()
    self.wtable.appendOp("group",result_col,*cols)

  def order(self, result_col, *cols):
    self.__uniquify()
    self.wtable.appendOp("order",result_col,*cols)

  def unique(self, *cols):
    self.wtable.unique(*cols)

  def set_src(self, src, *attr):
    self.src_col = src

  def set_dst(self, dst, *attr):
    self.dst_col = dst

  def set_edge_attr(self, *attr):
    pass

  def set_flag(self, flag, value):
    if flag == 'IS_MULTIGRAPH':
      self.is_multigraph = value
    elif flag == 'BIPARTITE':
      self.bipartite = value
    elif flag == 'DIRECTED':
      self.directed = value

  def set_flags(self, *flags):
    for fl in flags:
      self.set_flag(fl, True)

  def build_graph(self):
    """
    Builds a graph from the final working table, using the specified flags and attribute parameters
    Note: this function is just a placeholder for the moment
    """
    self.__uniquify()
    print "Created graph with " + str(self.size()) + " edges"

  def make_graph(self, instr_file):
    """Creates a graph from the given instruction file"""
    err_msg = "couldn't read instructions"
    self.uniquified = False
    with utils.ringo_open(instr_file, err_msg) as f:
      # Execute query
      try:
        for line in f:
          tokens = list(utils.get_tokens(line))
          {
            'SRC': self.set_src,
            'DST': self.set_dst,
            'EDGE_ATTR': self.set_edge_attr,
            'FLAGS': self.set_flags,
            'LOAD': self.load,
            'START': self.start,
            'LABEL': self.label,
            'JOIN': self.join,
            'SELECT': self.select,
            'COUNT': self.count,
            'GROUP': self.group,
            'ORDER': self.order
          }[tokens[0]](*tokens[1:])
      except KeyError:
        raise InvalidInstructionException('Incomplete query')
      self.build_graph()
    return

  def dump(self, num):
    if not self.wtable is None:
      self.wtable.dump(num,True)
      return True
    return False

  def size(self):
    if not self.wtable is None:
      return self.wtable.numrows()