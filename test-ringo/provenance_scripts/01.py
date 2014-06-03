import sys
import ringo


def generate(engine, filename0):
    table = engine.LoadTableTSV([('Src', 'int'), ('Dst', 'int')], filename0)
    return table

engine = ringo.Ringo()
files = ['data/soc-LiveJournal1_small.txt']
for i in xrange(min(len(files), len(sys.argv)-1)):
    files[i] = sys.argv[i+1]
table = generate(engine, *files)
