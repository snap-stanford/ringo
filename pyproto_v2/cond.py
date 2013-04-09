import pyparsing as pp
import operator as op
import utils

class Condition:
  """
  Condition parsing for the "select" operation
  """
  def __init__(self,cond):
    self.cond = cond
    self.root = self.parse() # parse the expression to a tree and store the root

  def parse(self):
    col = pp.Word(pp.alphanums)
    val = pp.Word(pp.alphanums)
    comp = pp.Regex('==|!=|<=|>=|<|>')
    cond = pp.Group(col + comp + val)
    expr = pp.operatorPrecedence(cond,[('&&',2,pp.opAssoc.LEFT),('||',2,pp.opAssoc.LEFT)])
    return expr.parseString(self.cond).asList()[0]

  def eval(self,rowdict):
    # NOTE: comparisons with "None" evaluate to True!
    return self.evalnode(self.root,rowdict)
  def evalnodeleft(self,node,rowdict):
    if not isinstance(node,list):
      return rowdict[node]
    return self.evalnode(node,rowdict)
  def evalnoderight(self,node,rowdict):
    if not isinstance(node,list):
      # Comparisons of the form Attribute1 <op> Attribute2 are considered
      # before comparisons of the form Attribute1 <op> Value
      # TODO: give a syntactic way of forcing a comparison of the form Attribute1 <op> Value when ambiguous
      try:
        return rowdict[node]
      except KeyError:
        return node
    return self.evalnode(node,rowdict)
  def evalnode(self,node,rowdict):
    # This function is used for both comparison and boolean operators.
    # (TODO: it should be possible to treat them differently, to improve readability)
    err = 'Wrong node format'
    if len(node) != 3:
      raise Exception(err)
    vleft = self.evalnodeleft(node[0],rowdict)
    vright = self.evalnoderight(node[2],rowdict)
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
        if isinstance(vleft,utils.Date):
          vright = utils.Date(vright)
      except ValueError:
        raise Exception(err)
    return {'&&':op.__and__,
            '||':op.__or__,
            '==':op.eq,
            '!=':op.ne,
            '>=':op.ge,
            '<=':op.le,
            '>':op.gt,
            '<':op.lt}.get(node[1])(vleft,vright)
