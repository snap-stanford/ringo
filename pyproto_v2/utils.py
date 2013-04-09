import time

class Date(object):
  def __init__(self,string):
    self.val = time.strptime(string.split('.')[0],'%Y-%m-%dT%H:%M:%S')
  def __str__(self):
    return time.strftime('%Y-%m-%dT%H:%M:%S',self.val)
  def __unicode__(self):
    return unicode(str(self))
  def __repr__(self):
    return str(self)
  def __eq__(self,other):
    return self.val == other.val
  def __ne__(self,other):
    return self.val != other.val
  def __le__(self,other):
    return self.val <= other.val
  def __ge__(self,other):
    return self.val >= other.val
  def __lt__(self,other):
    return self.val < other.val
  def __gt__(self,other):
    return self.val > other.val
  def __hash__(self):
    return hash(self.val)
  def __cmp__(self,other):
    if self < other:
      return -1
    elif self > other:
      return 1
    else:
      return 0