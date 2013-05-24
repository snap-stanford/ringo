import abc

class GraphEngine(object):
  """
  Graph creation engines should inherit from this abstract class
  """
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractmethod
  def load(self, filename, tablename = None):
    """Load table. Returns True if table was successfully loaded, False otherwise."""
    return