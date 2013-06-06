import operator as op
import pyutils
import pdb

OPERATORS = set(["==","!=",">=","<=",">","<","&&","||"])

class InvalidOperatorError(Exception):
  def __init__(self, msg = None):
    self.message = "Operator not found"
    if not msg is None:
      self.message += ": " + msg
    super(InvalidOperatorError, self).__init__(self.message)
class InvalidTreeError(Exception):
  def __init__(self):
    self.message = "Selection tree is not valid"
    super(InvalidTreeError, self).__init__(self.message)

class Operator(object):
  def __init__(self,name):
    try:
      self.function = {'&&':op.__and__,
                        '||':op.__or__,
                        '==':op.eq,
                        '!=':op.ne,
                        '>=':op.ge,
                        '<=':op.le,
                        '>':op.gt,
                        '<':op.lt}[name]
    except KeyError:
      raise InvalidOperatorError(name)

class Colname(object):
  def __init__(self,name):
    self.name = name

class Condition(object):
  """
  Condition parsing for the "select" operation
  """
  def __init__(self,prefix_expr):
    self.root,_ = self.parseTree(prefix_expr)

  def parseTree(self,prefix_expr):
    prefix_expr.reverse()
    return self.__parseTree(prefix_expr)

  def __parseTree(self,prefix_expr):
    """This function is used to build an evaluation tree from an expression given in prefix notation"""
    root = []
    head = prefix_expr.pop()
    if head in OPERATORS:
      subtree,prefix_expr = self.__parseTree(prefix_expr)
      root.append(subtree)
      root.append(Operator(head))
      subtree,prefix_expr  = self.__parseTree(prefix_expr)
      root.append(subtree)
    else:
      root.append(head)
    return root,prefix_expr

  def eval(self,rowdict):
    # NOTE: comparisons with "None" evaluate to True!
    return self.evalnode(self.root,rowdict)
  def evalchild(self,node,rowdict):
    if not isinstance(node,list):
      if type(node) == Colname:
        return rowdict[node.name]
      else:
        return node
    return self.evalnode(node,rowdict)
  def evalnode(self,node,rowdict):
    # This function is used for both comparison and boolean operators.
    # (TODO: it should be possible to treat them differently, to improve readability)
    err = 'Wrong node format'
    if len(node) == 1:
      return self.evalchild(node[0],rowdict)
    elif len(node) == 3:
      vleft = self.evalchild(node[0],rowdict)
      vright = self.evalchild(node[2],rowdict)
      # Convert the given string value to the appropriate type
      if vleft == None or vright == None:
        return False # Remove rows with None values
      if isinstance(vleft,bool):
        if not isinstance(vright,bool):
          raise Exception(err)
      else:
        try:
          if isinstance(vleft,(int,float)):
            vright = float(vright)
          if isinstance(vleft,pyutils.Date):
            vright = pyutils.Date(vright)
        except ValueError:
          raise Exception(err)
      if not type(node[1]) == Operator:
        raise InvalidTreeError()
      return node[1].function(vleft,vright) #TODO : lazy evaluation!
    else:
      raise InvalidTreeError()
