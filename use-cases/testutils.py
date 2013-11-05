import time

class Timer(object):
  def __init__(self, enabled = True):
    self.enabled = enabled
    self.time = time.time()
  def show(self, operation):
    if self.enabled:
      print '[%s]\tElapsed: %.2f seconds' % (operation, time.time() - self.time)
    self.time = time.time()

def dump(table, maxRows = None):
  colSpace = 25
  S = table.GetSchema()
  template = ""
  line = ""
  names = []
  types = []
  for i, attr in enumerate(S):
    template += "{%d: <%d}" % (i, colSpace)
    names.append(attr.GetVal1())
    types.append(attr.GetVal2())
    line += "-" * colSpace
  print template.format(*names)
  print line
  RI = table.BegRI()
  cnt = 0
  while RI < table.EndRI() and (maxRows is None or cnt < maxRows):
    elmts = []
    for c,t in zip(names,types):
      if t == 0: # int
        elmts.append(str(RI.GetIntAttr(c)))
      elif t == 1: # float
        elmts.append("{0:.5f}".format(RI.GetFltAttr(c)))
      elif t == 2: # string
        elmts.append(RI.GetStrAttr(c))
      else:
        raise NotImplementedError("unsupported column type")
    print template.format(*elmts)
    RI.Next()
    cnt += 1