import utils
import re
import pandas_graph_engine as pge

class InvalidQueryException(Exception):
  def __str__(self, buf):
    return "Invalid query: couldn't parse \"" + buf + "\""
class InternalParserError(Exception):
  def __str__(self):
    return "Error during parsing"

class Transformation(object):
  def __init__(self,name,*args):
    self.name = name # name of the transformation
    self.args = args # arguments (column names, tables, ...)

class Query(object):
  """
  A query object is used to store a graph description
  """
  def __init__(self, query_str = None):
    self.init_wtable = None # initial working table
    self.init_wcol = None # initial working column
    self.path_trsf = []
    self.filter_trsf = []
    self.src_attr = None
    self.dst_attr = None
    self.edge_attr = None
    self.flags = []
    self.num_anon = 0 # Counter for anonymous columns
    if not query_str is None:
      self.parse_query(query_str)

  def parse_query(self, query_str):
    field = None
    buf = ""
    for line in query_str:
      line = line.strip()
      if len(line) > 0:
        m = re.match(r"(\w+)\s*:(.*)", line)
        if m is None:
          buf += "," + line # This line continues the previous one
        else:
          self.process_field(field, buf) # Process previous field
          field = m.group(1) # Start reading field
          buf = m.group(2)
    self.process_field(field, buf)

  def process_field(self, field, buf):
    if not field is None:
      try:
        {
          'PATH': self.process_path,
          'FILTER': self.process_filter,
          'SRC_ATTR': self.process_src_attr,
          'DST_ATTR': self.process_dst_attr,
          'EDGE_ATTR': self.process_edge_attr,
          'FLAGS': self.process_flags
        }[field](buf.strip())
      except KeyError:
        print "Warning: Unrecognized field " + field

  def transformations(self):
    for trsf in self.path_trsf:
      yield trsf
    for trsf in self.filter_trsf:
      yield trsf

  def parse_table_col(self, string):
    m = re.match(r"(\w+)\.(\w+)(.*)", string)
    if m is None:
      raise InvalidQueryException(string)
    else:
      return m.group(1), m.group(2), m.group(3).strip()

  def parse_name(self, string):
    m = re.match(r"(\w+)(.*)", string)
    if m is None:
      raise InvalidQueryException(string)
    else:
      return m.group(1), m.group(2).strip()

  def parse_arguments(self, string):
    raw_args = map(lambda x: x.strip(), string.split(","))
    arguments = []
    for arg in raw_args:
      name, rest = self.parse_name(arg)
      if len(rest) > 0:
        raise InvalidQueryException(string)
      arguments.append(name);
    return arguments

  def path_parse_next(self, buf):
    m = re.match(r"(?#separator),?\s*"
                 r"(?#operator)(<=>|--|as\s+)"
                 r"(?#arguments)(.*?)"
                 r"(?#stop before next operation),?\s*(?=($|(<=>|--|\s+as\s*).*))", buf)
    if m is None:
      raise InvalidQueryException(buf)
    else:
      operator = m.group(1).strip()
      arguments = m.group(2).strip()
      if operator == "<=>":
        table, col, rest = self.parse_table_col(arguments)
        if len(rest) > 0:
          raise InvalidQueryException(rest)
        trsf = Transformation("JOIN", table, col)
      else:
        col, rest = self.parse_name(arguments)
        if len(rest) > 0:
          raise InvalidQueryException(rest)
        if operator == "--":
          trsf = Transformation("LINK", col)
        elif operator == "as":
          trsf = Transformation("LABEL", col)
        else:
          raise InternalParserError()
      self.path_trsf.append(trsf)
    return m.group(3).strip()

  def process_one_filter(self, buf):
    m_label = re.match(r"(.*)\s+as\s+(\w+)\s*", buf)
    if m_label is None:
      # TODO: parse the selector
      self.filter_trsf.append(Transformation("SELECT", buf))
    else:
      body = m_label.group(1).strip()
      label = m_label.group(2).strip()
      m_anon = re.match(r"(\w+)\(([\w,\s]*)\)", body)
      if not m_anon is None:
        operator = m_anon.group(1)
        arguments = self.parse_arguments(m_anon.group(2))
        if operator == "COUNT" or operator == "ORDER" or operator == "GROUP":
          self.filter_trsf.append(Transformation(operator, label, *arguments))
        else:
          raise InvalidQueryException(body)

  def filter_parse_next(self, buf):
    cnt = 0
    pos = 0
    for c in buf:
      if c == '(':
        cnt += 1
      elif c == ')':
        cnt -= 1
        if cnt < 0:
          raise InvalidQueryException(buf)
      elif c == ',' and cnt == 0:
        break
      pos += 1
    self.process_one_filter(buf[:pos].strip())
    return buf[pos+1:].strip()

  def process_path(self, buf):
    buf = buf.strip()
    self.init_wtable, self.init_wcol, buf = self.parse_table_col(buf)
    while len(buf) > 0:
      buf = self.path_parse_next(buf)

  def process_filter(self, buf):
    while len(buf) > 0:
      buf = self.filter_parse_next(buf)

  def process_src_attr(self, buf):
    self.src_attr = self.parse_arguments(buf)

  def process_dst_attr(self, buf):
    self.dst_attr = self.parse_arguments(buf)

  def process_edge_attr(self, buf):
    self.edge_attr = self.parse_arguments(buf)

  def process_flags(self, buf):
    self.flags = self.parse_arguments(buf)

  def show_transformations(self):
    for trsf in self.transformations():
      print trsf.name + "(" + ", ".join(trsf.args) + ")"

  def show_attr(self):
    for trsf in self.transformations():
      print trsf.name + "(" + ", ".join(trsf.args) + ")"

class Ringo(object):
  """
  Main class - allows the user to import a dataset and create graphs
  """
  def __init__(self, engine = "PANDAS"):
    self.form = [None]*5
    if engine == "PANDAS":
      self.engine = pge.PandasGraphEngine()
    else:
      raise NotImplementedError()

  def load(self, filename, tablename = None):
    return self.engine.load(filename, tablename)

  def check_query(self, query):
    # TODO: Check that query is well-defined and that all tables are loaded
    pass

  def run_query(self, query):
    self.check_query(query)
    print "Received query. The transformations are:"
    query.show_transformations()
    print query.src_attr
    print query.dst_attr
    print query.edge_attr
    print query.flags

  def make_graph(self, filename, query = None):
    if query is None:
      with utils.ringo_open(filename) as (f,error):
        if error:
          print "IOError:" + error
        else:
          query = f.readlines()
    query_obj = Query()
    query_obj.parse_query(query)
    return self.run_query(query_obj)