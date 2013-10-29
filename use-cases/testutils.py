import time

class Timer(object):
  def __init__(self, enabled = True):
    self.enabled = enabled
    self.time = time.time()
  def show(self, operation):
    if self.enabled:
      print '[%s]\tElapsed: %.2f seconds' % (operation, time.time() - self.time)
    self.time = time.time()