import os, sys
sys.path.insert(1, "..")
sys.path.append("../../ringo-engine-python")
import ringo

def generate(engine,filename0,filename1):
    t1=engine.LoadTableTSV([('PostId', 'int'), ('UserId', 'int'), ('AnswerId', 'int')],filename0)
    t2=engine.LoadTableTSV([('PostId', 'int'), ('Tag', 'string')],filename1)
    engine.Select(t2,'Tag = python',CompConstant=True)
    t3=engine.Join(t1,t2,'PostId','PostId')
    t4=engine.Join(t3,t1,'AnswerId','PostId')
    return t4

engine=ringo.Ringo()

srcdir = sys.argv[1]
dstdir = sys.argv[2] if len(sys.argv) >= 3 else None
if not dstdir is None:
  try:
    os.makedirs(dstdir)
  except OSError:
    pass

out = generate(engine, os.path.join(srcdir, 'posts.tsv'), os.path.join(srcdir, 'tags.tsv'))
engine.DumpTableContent(out, 20)
