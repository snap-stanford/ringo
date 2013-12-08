import sys
sys.path.insert(1, "..")
sys.path.append("../../ringo-engine-python")
import ringo

[(t1_ColName1, t1_ColType1), (t1_ColName2, t1_ColType2), (t1_ColName3, t1_ColType3), (t1_ColName4, t1_ColType4)] = [('PostId', 'int'), ('UserId', 'int'), ('AnswerId', 'int'), ('CreationDate', 'string')]
[(t2_ColName1, t2_ColType1), (t2_ColName2, t2_ColType2)] = [('PostId', 'int'), ('Tag', 'string')]

def generate(engine,filename0, filename1, filename2):
    t1 = engine.LoadTableTSV([(t1_ColName1, t1_ColType1), (t1_ColName2, t1_ColType2), (t1_ColName3, t1_ColType3), (t1_ColName4, t1_ColType4)], filename0)
    t2 = engine.LoadTableTSV([(t2_ColName1, t2_ColType1), (t2_ColName2, t2_ColType2)], filename1)
    t2 = engine.Select(t2, 'Tag = python', CompConstant=True)
    t3 = engine.Join(t1, t2, t1_ColName1, t2_ColName1)
    t4 = engine.Join(t3, t1, 'AnswerId', t1_ColName1)
    graph = engine.ToGraph(t4, '1_2.1.UserId', '1.UserId')
    (HTHub, HTAuth) = engine.GetHits(graph)
    t5 = engine.TableFromHashMap(HTAuth, 'UserId', 'Authority')
    t5 = engine.Order(t5, ['Authority'], Asc=False)
    t5 = engine.SaveTableTSV(t5, filename2)
    return t5

engine = ringo.Ringo()
files = ['input/posts.tsv', 'input/tags.tsv', './experts.tsv']
for i in xrange(min(len(files), len(sys.argv)-1)):
    files[i] = sys.argv[i+1]
t5 = generate(engine, *files)
engine.DumpTableContent(t5, 20)
engine.ShowMetadata(t5)

