from contextlib import contextmanager
import os
import re

class FileOpenError(Exception):
  def __init__(self, filename, error, msg = None):
    self.message = "Error opening file \"" + filename + "\": " + str(error)
    if not msg is None:
      self.message += " (" + msg + ")"
    super(FileOpenError, self).__init__(self.message)

@contextmanager
def ringo_open(filename, msg = None, mode="r"):
  try:
    f = open(filename, mode)
  except IOError, error:
    raise FileOpenError(filename, error, msg)
  else:
    try:
      yield f
    finally:
      f.close()

class Found(Exception): pass

def get_free_prefix(strings):
  """Returns a string that is not a prefix for any of the given strings"""
  num = 0
  prefix = "__" + str(num) + "_"
  for s in strings:
    while s.startswith(prefix):
      num += 1
      prefix = "__" + str(num) + "_"
  return prefix

def get_name_for_table(filename):
  basename = os.path.basename(filename)
  tablename, _ = os.path.splitext(basename)
  tablename = "_".join(tablename.split("."))
  return "_".join(tablename.split(" "))

def get_tokens(string):
  string = string.rstrip()
  quote_cnt = 0
  last = -1
  for pos,c in enumerate(string):
    if c == "\"":
      quote_cnt += 1
    elif quote_cnt % 2 == 0 and c == " ":
      if pos - last > 1:
        yield string[last+1:pos]
      last = pos
  if quote_cnt % 2 == 0 and len(string) - last > 1:
    yield string[last+1:]

def to_safe(name, id):
  return "__" + name + "_" + str(id)
def from_safe(string):
  m = re.match(r"^__(\w+)_(\d+)$", string)
  return m.group(1), m.group(2)