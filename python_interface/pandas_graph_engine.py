import pandas as pd
import graph_engine as ge
import utils
import copy
import operator
import pdb

WTABLE_NAME = "wtable"
SRCCOL_NAME = "source"

class InvalidInstructionException(Exception):
  def __init__(self, msg = None):
    self.message = "Invalid instruction"
    if not msg is None:
      self.message += ": " + msg
    super(InvalidInstructionException, self).__init__(self.message)

class Table(object):
  """Object used to store a PANDAS data frame, along with a column naming datastructure"""
  def __init__(self, filename = None, tablename = None):
    self.labels = {}
    self.reverse_labels = {}
    if not filename is None:
      self.name = utils.get_name_for_table(filename) if tablename is None else tablename
      self.dataframe = pd.read_csv(filename,sep='\t',error_bad_lines=False)
      for col in self.dataframe.columns:
        self.labels[col] = [col]
        self.reverse_labels[col] = col
      self.__setup_names()

  def __get_col_name(self, label):
    if not label in self.reverse_labels:
      raise InvalidInstructionException("Couldn't find column \"" + label + "\" in table \"" + self.name + "\"")
    return self.reverse_labels[label]

  def __get_selection_val(self, string):
    string = string.strip()
    if string[0] == "\"" and string[-1] == "\"":
      return string[1:-1]
    else:
      try:
        return int(string)
      except ValueError:
        try:
          return float(string)
        except ValueError:
          if not string in self.reverse_labels:
            raise InvalidInstructionException("Couldn't find column \"" + string + "\"")
          return self.dataframe[self.reverse_labels[string]]

  def __eval_select(self, tree):
    if len(tree) == 0:
      raise InvalidInstructionException("Malformed selection clause")
    head = tree.pop()
    if head == "&&" or head == "||":
      boolean1, tree = self.__eval_select(tree)
      boolean2, tree = self.__eval_select(tree)
      if head == "&&": return boolean1 & boolean2, tree
      if head == "||": return boolean1 | boolean2, tree
    try:
      op = {
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        "<=": operator.le,
        ">": operator.gt,
        "<": operator.lt
      }[head]
    except KeyError:
      raise InvalidInstructionException("Malformed selection clause: invalid comparison")
    try:
      left = self.__get_selection_val(tree.pop())
      right = self.__get_selection_val(tree.pop())
    except IndexError:
      raise InvalidInstructionException("Malformed selection clause")
    return op(left,right), tree

  def __init_grouping(self, result_col, cols):
    aggcol = None
    if not result_col is None:
      # Setup new column name
      aggcol = utils.to_safe(self.name, len(self.labels))
      self.labels[aggcol] = [result_col]
      self.reverse_labels[result_col] = aggcol
    # Find real column names
    realcols = []
    for col in cols:
      try:
        realcols.append(self.reverse_labels[col])
      except KeyError:
        raise InvalidInstructionException("Couldn't find column \"" + col + "\"")
    return aggcol, realcols

  def __setup_names(self):
    """Rebuilds all column names to put them into the form __<tablename>_<idx>"""
    for idx,col in enumerate(self.dataframe.columns):
      new_name = utils.to_safe(self.name, idx)
      self.rename(col, new_name)

  def label(self, column, name):
    """Adds the given name to the specified column"""
    if not column in self.reverse_labels:
      raise InvalidInstructionException("Couldn't find column " + column)
    # Remove existing binding for name
    if name in self.reverse_labels:
      old_column = self.reverse_labels[name]
      self.labels[old_column].remove(name)
    # Set new label
    real_column = self.reverse_labels[column]
    self.labels[real_column].append(name)
    self.reverse_labels[name] = real_column

  def rename(self, old_name, new_name):
    """Changes the column name from old_name to new_name in the underlying dataframe"""
    new_columns = []
    # Update list of columns
    for col in self.dataframe.columns:
      if col == old_name:
        new_columns.append(new_name)
      else:
        new_columns.append(col)
    self.dataframe.columns = new_columns
    # Update labels
    labels = self.labels.pop(old_name)
    self.labels[new_name] = labels
    for l in labels:
      self.reverse_labels[l] = new_name

  def copy(self, tablename):
    table_copy = Table()
    table_copy.dataframe = self.dataframe.copy() # TODO: check that deep copy is not needed
    table_copy.labels = copy.deepcopy(self.labels)
    table_copy.reverse_labels = self.reverse_labels.copy()
    table_copy.name = tablename
    table_copy.__setup_names()
    return table_copy

  def join(self, col1, table, col2):
    realname1 = self.__get_col_name(col1)
    realname2 = table.__get_col_name(col2)
    # Join tables
    self.dataframe = pd.merge(self.dataframe, table.dataframe, left_on=realname1, right_on=realname2)
    # Setup the new labels
    for col,labels in table.labels.iteritems():
      for l in labels:
        if l in self.reverse_labels:
          # Remove ambiguous label
          old_name = self.reverse_labels[l]
          self.labels[old_name].remove(l)
        self.reverse_labels[l] = col
      self.labels[col] = labels
    self.__setup_names()

  def select(self, tree):
    ltree = list(tree)
    ltree.reverse()
    self.dataframe = self.dataframe[self.__eval_select(ltree)[0]]

  def count(self, result_col, *cols):
    aggcol, realcols = self.__init_grouping(result_col, cols)
    # Generate new column
    grouped = self.dataframe.groupby(realcols)
    counts = grouped.size()
    counts.name = aggcol
    # Add column to data frame
    counts = pd.DataFrame(counts)
    self.dataframe = pd.merge(self.dataframe, counts, left_on=realcols, right_index=True, sort=False)

  def group(self, result_col, *cols):
    aggcol, realcols = self.__init_grouping(result_col, cols)
    # Generate new column
    grouped = self.dataframe[realcols].groupby(realcols)
    groups = grouped[realcols[0]].agg(lambda df: 0)
    groups.name = aggcol
    # Number groups
    groups[:] = range(len(groups.index))
    # Add column to data frame
    groups = pd.DataFrame(groups)
    self.dataframe = pd.merge(self.dataframe, groups, left_on=realcols, right_index=True, sort=False)

  def order(self, result_col, *cols):
    aggcol, realcols = self.__init_grouping(result_col, cols)
    self.dataframe = self.dataframe.sort(realcols, inplace=True).reset_index()
    self.dataframe.pop('index')
    self.dataframe[aggcol] = self.dataframe.index

  def unique(self, *cols):
    _, realcols = self.__init_grouping(None, cols)
    grouped = self.dataframe.groupby(realcols)
    indexes = grouped[realcols[0]].agg(lambda group: group.index[0])
    self.dataframe = self.dataframe.ix[indexes, :]


class PandasGraphEngine(ge.GraphEngine):
  """
  Graph creation engine based on the PANDAS library
  """
  def __init__(self):
    self.tables = {}
    self.labels = {}
    self.wtable = None
    self.is_multigraph = False
    self.bipartite = False
    self.directed = False
    self.finalized_path = False

  def __finalize_path(self):
    """Calls unique() if the flag IS_MULTIGRAPH is not present"""
    if not self.is_multigraph:
      self.wtable.unique(self.src_col, self.dst_col)
    self.finalized_path = True

  def reset(self):
    self.__init__() # Maybe we could keep tables in memory

  def load(self, filename, tablename = None):
    if tablename is None:
      tablename = utils.get_name_for_table(filename)
    # If a table with the same name already exists, it is overwritten
    self.tables[tablename] = Table(filename)

  def start(self, tablename):
    if not tablename in self.tables:
      raise InvalidInstructionException("Couldn't find table \"" + tablename + "\"")
    self.wtable = self.tables[tablename].copy(WTABLE_NAME)
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
    if not self.finalized_path:
      self.__finalize_path()
    self.wtable.select(tree)

  def count(self, result_col, *cols):
    if not self.finalized_path:
      self.__finalize_path()
    self.wtable.count(result_col, *cols)

  def group(self, result_col, *cols):
    if not self.finalized_path:
      self.__finalize_path()
    self.wtable.group(result_col, *cols)

  def order(self, result_col, *cols):
    if not self.finalized_path:
      self.__finalize_path()
    self.wtable.order(result_col, *cols)

  def set_src(self, src, *attr):
    self.src_col = src

  def set_dst(self, dst, *attr):
    self.dst_col = dst

  def set_edge_attr(self, *attr):
    pass

  def set_flags(self, *flags):
    for fl in flags:
      if fl == 'IS_MULTIGRAPH':
        self.is_multigraph = True
      elif fl == 'BIPARTITE':
        self.bipartite = True
      elif fl == 'DIRECTED':
        self.directed = True

  def build_graph(self):
    """
    Builds graph from final working table, using the specified flags and attribute parameters
    Note: this function is just a placeholder for the moment
    """
    print "Created graph with " + str(len(self.wtable.dataframe.index)) + " edges"

  def make_graph(self, instr_file):
    """Creates a graph from the given instruction file"""
    err_msg = "couldn't read instructions"
    self.finalized_path = False
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