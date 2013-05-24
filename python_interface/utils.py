from contextlib import contextmanager

@contextmanager
def ringo_open(filename, mode="r"):
  try:
    f = open(filename, mode)
  except IOError, error:
    yield None, error
  else:
    try:
      yield f, None
    finally:
      f.close()