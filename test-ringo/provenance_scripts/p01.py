import sys
import ringo


def generate(engine):
    G = engine.GenRndGnm(engine.PUNGraph, 100, 100)
    G = engine.AddSelfEdges(G)
    G.GetNodes()
    return G

engine = ringo.Ringo()
files = []
for i in xrange(min(len(files), len(sys.argv)-1)):
    files[i] = sys.argv[i+1]
G = generate(engine, *files)
