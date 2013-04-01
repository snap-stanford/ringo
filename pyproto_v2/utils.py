import time

class Date():
  def __init__(self,string):
    self.val = time.strptime(string.split('.')[0],'%Y-%m-%dT%H:%M:%S')
  def __str__(self):
    return time.strftime('%Y-%m-%dT%H:%M:%S',self.val)
  def __unicode__(self):
    return unicode(str(self))
  def __repr__(self):
    return str(self)