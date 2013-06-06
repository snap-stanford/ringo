import utils
import re
import pandas_graph_engine as pge
import python_graph_engine as pyge
import itertools
import os
import pdb

class InvalidQueryException(Exception):
  def __init__(self, buf):
    self.message = "Invalid query: couldn't parse \"" + buf + "\""
    super(InvalidQueryException, self).__init__(self.message)
class InternalParserError(Exception):
  def __init__(self):
    self.message = "Error during parsing"
    super(InternalParserError, self).__init__(self.message)

class Instruction(object):
  def __init__(self,name,*args):
    self.name = name # name of the instruction
    self.args = args # arguments (column names, tables, ...)
  def __str__(self):
    return self.name + "(" + ", ".join(self.args) + ")"

class Query(object):
  """
  A query object is used to store a graph description
  """
  def __init__(self, query_str = None, tablefiles = None):
    self.wtable = None # initial working table
    self.wcol = None # initial working column
    self.load_instr = []
    self.path_instr = []
    self.filter_instr = []
    self.src_col = None
    self.dst_col = None
    self.src_attr = []
    self.dst_attr = []
    self.edge_attr = []
    self.flags = []
    self.num_anonymous = 0 # Counter for anonymous columns
    self.instr_filename = "__ringo_query.i"
    # Add loading instructions
    if not tablefiles is None:
      for tablename, filename in tablefiles.iteritems():
        self.load_instr.append(Instruction("LOAD", filename, tablename))
    # Parse query
    if not query_str is None:
      self.parse_query(query_str)

  def __parse_table_col(self, string):
    m = re.match(r"^(\w+)\.(\w+)(.*)", string)
    if m is None:
      raise InvalidQueryException(string)
    else:
      return m.group(1), m.group(2), m.group(3).strip()

  def __parse_name(self, string):
    m = re.match(r"^(\w+)(.*)", string)
    if m is None:
      raise InvalidQueryException(string)
    else:
      return m.group(1), m.group(2).strip()

  def __parse_arguments(self, string):
    raw_args = list(itertools.chain(*map(lambda x: x.split(),string.split(","))))
    arguments = []
    for arg in raw_args:
      name, rest = self.__parse_name(arg)
      if len(rest) > 0:
        raise InvalidQueryException(string)
      arguments.append(name);
    return arguments

  def __get_first_expr(self, buf, *sep):
    """
    Returns the first well-formed expression occuring before any of the given separators.
    "well-formed" means that the number of opening and closing parentheses is the same. 
    The outermost parentheses are removed from the expression, if they exist.
    """
    head = None
    op = None
    tail = ""
    cnt = 0
    pos = 0
    try:
      for c in buf:
        if c == '(':
          cnt += 1
        elif c == ')':
          cnt -= 1
          if cnt < 0:
            raise InvalidQueryException(buf)
        elif cnt == 0:
          for s in sep:
            if buf[pos:pos+len(s)] == s:
              op = s
              raise utils.Found
        pos += 1
    except utils.Found:
      tail = buf[pos+len(op):].strip()
    head = buf[:pos].strip()
    if head[0] == '(' and head[-1] == ')':
      head = head[1:-1]
    return head, op, tail

  def __get_label(self):
    """Returns a unique label"""
    self.num_anonymous += 1
    return "__ringo_anon_" + str(self.num_anonymous)

  def __parse_operator(self, buf, anon_instr, label = None):
    """Parses operators written as OPERATOR(ARG1, ARG2, ...)"""
    m_anon = re.match(r"(\w+)\(([\w,\s]*)\)", buf)
    if not m_anon is None:
      operator = m_anon.group(1)
      arguments = self.__parse_arguments(m_anon.group(2))
      if operator == "COUNT" or operator == "ORDER" or operator == "GROUP":
        if label is None:
          label = self.__get_label()
        anon_instr.append(Instruction(operator, label, *arguments))
        return label
      else:
        raise InvalidQueryException(buf)    

  def __parse_atom(self, buf, anon_instr):
    """Parses the given atomic expression. Supports chained atoms, such as VAL1 > VAL2 > VAL3"""
    ops = ['==', '!=', '>=', '<=', '>', '<'] # The order matters, because the first matching separator is used (eg '>' must be after '>=')
    head1, sep1, tail1 = self.__get_first_expr(buf, *ops)
    label = self.__parse_operator(head1, anon_instr)
    if not label is None:
      head1 = label
    if sep1 is None:
      raise InvalidQueryException(buf)
    acc = sep1 + " " + head1
    while len(tail1) > 0:
      head2, sep2, tail2 = self.__get_first_expr(tail1, *ops)
      label = self.__parse_operator(head2, anon_instr)
      if not label is None:
        head2 = label
      acc += " " + head2 # Close previous atom
      if sep2 is None:
        break
      else:
        acc = " ".join(["&&", acc, sep2, head2]) # Start new atom
        tail1 = tail2
    return acc

  def __parse_selector(self, buf, anon_instr):
    """Parse the selection query and returns its formulation in prefix notation"""
    head, sep, tail = self.__get_first_expr(buf, '&&', '||')
    if not sep is None:
      return sep + " " + self.__parse_selector(head, anon_instr) + " " + self.__parse_selector(tail, anon_instr)
    else:
      if len(head) < len(buf):
        return self.__parse_selector(head, anon_instr)
      else:
        # Reached stationary point: the expression should be an atom
        return self.__parse_atom(buf, anon_instr)


  def __process_one_filter(self, buf):
    m_label = re.match(r"^(.*)\s+as\s+(\w+)\s*", buf)
    if m_label is None:
      sel_desc = self.__parse_selector(buf, self.filter_instr)
      self.filter_instr.append(Instruction("SELECT", sel_desc))
    else:
      body = m_label.group(1).strip()
      label = m_label.group(2).strip()
      m_anon = re.match(r"(\w+)\(([\w,\s]*)\)", body)
      if not m_anon is None:
        operator = m_anon.group(1)
        arguments = self.__parse_arguments(m_anon.group(2))
        if operator == "COUNT" or operator == "ORDER" or operator == "GROUP":
          self.filter_instr.append(Instruction(operator, label, *arguments))
        else:
          raise InvalidQueryException(body)

  def __path_parse_next(self, buf):
    m = re.match(r"(?#operator)^\s*(=>|->|(?:as\s+))"
                 r"(?#arguments)(.*?)"
                 r"(?#stop before next operation)(?=($|(=>|->|\s+as\s+).*))", buf)
    if m is None:
      raise InvalidQueryException(buf)
    else:
      operator = m.group(1).strip()
      arguments = m.group(2).strip()
      if operator == "=>":
        table, col, rest = self.__parse_table_col(arguments)
        if len(rest) > 0:
          raise InvalidQueryException(rest)
        self.path_instr.append(Instruction("JOIN", self.wcol, table, col))
        self.wcol = col
        self.dst_col = col
      else:
        col, rest = self.__parse_name(arguments)
        if len(rest) > 0:
          raise InvalidQueryException(rest)
        if operator == "->":
          self.wcol = col
          self.dst_col = col
        elif operator == "as":
          self.path_instr.append(Instruction("LABEL", self.wcol, col))
          self.wcol = col
          self.dst_col = col
        else:
          raise InternalParserError()
    return m.group(3).strip()

  def __filter_parse_next(self, buf):
    head, sep, tail = self.__get_first_expr(buf, ',')
    self.__process_one_filter(head)
    return tail

  def __process_path(self, buf):
    buf = buf.strip()
    self.wtable, self.wcol, buf = self.__parse_table_col(buf)
    self.src_col = self.wcol
    self.path_instr.append(Instruction("START",self.wtable))
    while len(buf) > 0:
      buf = self.__path_parse_next(buf)

  def __process_filter(self, buf):
    while len(buf) > 0:
      buf = self.__filter_parse_next(buf)

  def __process_src_attr(self, buf):
    self.src_attr = self.__parse_arguments(buf)

  def __process_dst_attr(self, buf):
    self.dst_attr = self.__parse_arguments(buf)

  def __process_edge_attr(self, buf):
    self.edge_attr = self.__parse_arguments(buf)

  def __process_flags(self, buf):
    self.flags = self.__parse_arguments(buf)

  def show_instructions(self):
    for instr in self.instructions():
      print instr

  def write_attr(self, f, category, attributes):
    if len(attributes) > 0:
      f.write(category + " " + " ".join(attributes) + "\n")

  def write_instr_file(self):
    """Creates the instruction file to be passed to the graph engine (.i file)"""
    err_msg = "couldn't write query"
    with utils.ringo_open(self.instr_filename, err_msg, "w") as f:
      self.write_attr(f, "SRC", [self.src_col] + self.src_attr)
      self.write_attr(f, "DST", [self.dst_col] + self.dst_attr) # TODO: Depends on the flags! There might be some logic to put here
      self.write_attr(f, "EDGE_ATTR", self.edge_attr)
      self.write_attr(f, "FLAGS", self.flags)
      for instr in self.instructions():
        f.write(instr.name + " " + " ".join(instr.args) + "\n")

  def __process_field(self, field, buf):
    if not field is None:
      try:
        {
          'PATH': self.__process_path,
          'FILTER': self.__process_filter,
          'SRC_ATTR': self.__process_src_attr,
          'DST_ATTR': self.__process_dst_attr,
          'EDGE_ATTR': self.__process_edge_attr,
          'FLAGS': self.__process_flags
        }[field](buf.strip())
      except KeyError:
        print "Warning: Unrecognized field " + field

  def instructions(self):
    for instr in self.load_instr:
      yield instr
    for instr in self.path_instr:
      yield instr
    for instr in self.filter_instr:
      yield instr

  def parse_query(self, query_str):
    field = None
    buf = ""
    for line in query_str:
      line = line.strip()
      if len(line) > 0:
        m = re.match(r"(\w+)\s*:(.*)", line)
        if m is None:
          # This line continues the previous one
          if field == 'PATH':
            buf += " " + line
          else:
            buf += ", " + line
        else:
          self.__process_field(field, buf) # Process previous field
          field = m.group(1) # Start reading field
          buf = m.group(2)
    self.__process_field(field, buf)

class Ringo(object):
  """
  Main class - allows the user to import a dataset and create graphs
  """
  def __init__(self, engine = "PANDAS"):
    self.tablefiles = {}
    self.form = [None]*5
    if engine == "PANDAS":
      self.engine = pge.PandasGraphEngine()
    elif engine == "PYTHON":
      self.engine = pyge.PythonGraphEngine()
    else:
      raise NotImplementedError()

  def check_query(self, query):
    # TODO: Check that query is well-defined and that all tables are loaded?
    pass

  def run_query(self, query):
    self.check_query(query)
    self.engine.make_graph(query.instr_filename)

  def add_table(self, filename, tablename = None):
    """
    Adds a new table for the dataset. filename is the name of the file containing
    the table data, and tablename is an optional name for the table. If no 
    name is given, the table name is derived from the name of the file
    (without the extension). The file should be a tab-separated file, and the
    first line of the file should contain the column names.
    """
    if tablename is None:
      tablename = utils.get_name_for_table(filename)
    err_msg = "cannot load table"
    with utils.ringo_open(filename, err_msg):
      #if tablename in self.tablefiles:
      #   print "Table with this name already exists. Changing the source file"
      self.tablefiles[tablename] = filename

  def make_graph(self, filename = None, query = None, keep_instructions = False):
    """Creates a graph from the given query, or from the current working table / working column
    if no query has been specified. The query may be passed via a file (with the filename argument)
    or as a string (via the query argument)"""
    self.engine.reset()
    if query is None:
      with utils.ringo_open(filename) as f:
        query = f.readlines()
    query_obj = Query(query, self.tablefiles)
    if not filename is None:
      query_obj.instr_filename = filename + ".i"
    query_obj.write_instr_file()
    self.check_query(query_obj)
    self.engine.make_graph(query_obj.instr_filename)
    if not keep_instructions:
      os.remove(query_obj.instr_filename)


  """
  The following functions are here as a convenience for testing. They can be used
  to call the graph engine methods directly, e.g. for building a graph manually 
  without specifying a full query. These functions use the working column abstraction
  whenever it makes sense (the graph engine itself has no knowledge of the working column)
  """
  # TODO: These functions should give some feedback to the user

  def load(self, filename, tablename=None):
    """
    Loads a table into memory.
    """
    self.engine.load(filename, tablename)    

  def start(self, tablename, start_col):
    """
    Should be called to set the state of the engine at the beginning of a query.
    Sets the initial working table (at the beginning of a query execution), and the
    initial working column. tablename is the name of the initial working table, 
    start_col is the name of the initial working column.
    All activated flags in the engine are discarded (but the tables remain in memory)
    """
    self.wcol = start_col
    self.wtable = tablename
    self.engine.reset()
    self.engine.set_src(start_col)
    self.engine.start(tablename)
    return

  def link(self, col):
    """Changes the current working column."""
    self.wcol = col

  def label(self, name):
    """User interface for label()"""
    self.engine.label(self.wcol, name)

  def join(self, tablename, col):
    """User interface for join(). The join() method of the engine is called with 
    the current working column as col1, and col a col2"""
    self.engine.join(self.wcol, tablename, col)

  def select(self, *tree):
    """User interface for select()"""
    self.engine.select(*tree)

  def count(self, result_col, *cols):
    """User interface for count()"""
    self.engine.count(result_col, cols)

  def group(self, result_col, *cols):
    """User interface for group()"""
    self.engine.group(result_col, cols)

  def order(self, result_col, *cols):
    """User interface for order()"""
    self.engine.order(result_col, cols)

  def unique(self, *cols):
    """User interface for unique()"""
    self.engine.unique(*cols)

  def set_src(self, src, *attr):
    """User interface for set_src()"""
    self.engine.set_src(src, attr)

  def set_dst(self, dst, *attr):
    """User interface for set_dst()"""
    self.engine.set_dst(dst, attr)

  def set_edge_attr(self, *attr):
    """User interface for set_edge_attr()"""
    self.engine.set_edge_attr(attr)

  def set_flag(self, flag, value):
    """User interface for set_flag()"""
    self.engine.set_flag(flag, value)

  def build_graph(self):
    """User interface for build_graph()"""
    self.engine.build_graph()

  def dump(self, num=10):
    """Dumps the num first rows from the working table"""
    if not self.engine.dump(num):
      print "Working table not set"

  def getSize(self):
    return self.engine.size()