import abc

class GraphEngine(object):
  """
  Graph creation engines should inherit from this abstract class
  """
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractmethod
  def load(self, filename, tablename = None):
    """
    Loads a table into memory. filename is the name of the file containing
    the table data, and tablename is an optional name for the table. If no 
    name is given, the table name is derived from the name of the file
    (without the extension). The file should be a tab-separated file, and the
    first line of the file should contain the column names.
    """
    return

  @abc.abstractmethod
  def make_graph(self, instr_file):
    """Creates a graph from the given instruction file"""
    return

  @abc.abstractmethod
  def start(self, tablename):
    """
    Sets the initial working table (at the beginning of a query execution).
    tablename is the name of the initial working table.
    """
    return

  @abc.abstractmethod
  def reset(self, tablename):
    """
    Resets the state of the graph engine. Loaded tables remain in memory.
    """
    return

  @abc.abstractmethod
  def label(self, column, name):
    """
    Adds a label to a column of the working table.
    The column argument is the column name, and the name argument is the new label.
    """
    return

  @abc.abstractmethod
  def join(self, col1, tablename, col2):
    """
    Performs an equijoin between two tables. The first table is the working table,
    and tablename is the name of the second table. The equijoin is based on equality
    between the values in the column col1 of the working table, and the column col2
    of the other table.
    """
    return

  @abc.abstractmethod
  def select(self, *tree):
    """
    Selects only the rows that satisfy the given predicate. The predicate is 
    specified as a binary tree written in prefix notation.
    """
    return

  @abc.abstractmethod
  def count(self, result_col, *cols):
    """
    For each row, computes the number of rows that coincide on all values 
    in the columns cols. Writes the result in result_col.
    """
    return

  @abc.abstractmethod
  def group(self, result_col, *cols):
    """
    Groups the rows according to the values in the columns cols,
    and writes the group number of each row in the column result_col
    """
    return

  @abc.abstractmethod
  def order(self, result_col, *cols):
    """
    Finds the lexicographic ordering of the rows with respect to the columns cols,
    and writes the rank of each row in the column result_col
    """
    return

  @abc.abstractmethod
  def set_src(self, src, *attr):
    """
    Sets the attributes of the source column
    """
    return

  @abc.abstractmethod
  def set_dst(self, dst, *attr):
    """
    Sets the attributes of the destination column
    """
    return

  @abc.abstractmethod
  def set_edge_attr(self, *attr):
    """
    Sets the edge attributes
    """
    return

  @abc.abstractmethod
  def set_flag(self, flag, value):
    """
    Sets the value of a flag (IS_MULTIGRAPH, BIPARTITE, DIRECTED)
    """
    return

  @abc.abstractmethod
  def build_graph(self):
    """
    Builds a graph from the final working table, using the specified flags and attribute parameters
    """
    return

  @abc.abstractmethod
  def dump(self, num):
    """
    Dumps the first num rows of the working table. Returns False if the working table is not defined, True otherwise.
    """
    return

  @abc.abstractmethod
  def size(self):
    """
    Returns the current size of the working table (or None if the working table is not defined)
    """
    return

  @abc.abstractmethod
  def unique(self,*cols):
    """
    Retains exactly one row for each distinct joint assignment to the values in the columns cols.
    """
    return