import abc

class GraphEngine(object):
  """
  Graph creation engines should inherit from this abstract class
  """
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractmethod
  def make_graph(self, instr_file):
    """Creates a graph from the given instruction file"""
    return