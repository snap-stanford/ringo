import sys
sys.path.append("../ringo-engine-python/")
import ringo

r = ringo.Ringo()
G = r.GenRndGnm(r.PUNGraph,100,100)
G.Save('test')

G2 = r.Load('test')
G2.AddSelfEdges()
print G2.GetNodes()
G2.GenerateProvenance('provenance_scripts/p01.py')
