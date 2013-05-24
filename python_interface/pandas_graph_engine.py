import pandas as pd
import graph_engine as ge

class PandasGraphEngine(ge.GraphEngine):
  """
  Graph creation engine based on the PANDAS library
  """
  def __init__(self):
    self.tables = {}

  def load(self, filename, tablename = None):
    if tablename is None:
      tablename = filename
    try:
      self.tables[tablename] = pd.read_csv(filename,sep='\t',error_bad_lines=False)
      return True
    except Exception:
      return False