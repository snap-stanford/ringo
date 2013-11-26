import sys
sys.path.insert(1, "..")
sys.path.append("../../ringo-engine-python")
import ringo

def generate(engine,filename0, filename1, filename2):
    t1 = engine.LoadTableTSV([('PostId', 'int'), ('UserId', 'int'), ('AnswerId', 'int')], filename0)
    t2 = engine.LoadTableTSV([('PostId', 'int'), ('Tag', 'string')], filename1)
    #need to make this add an list, and have extra param on this select to make it not in place
    t2 = engine.Select(t2, 'Tag = java', CompConstant=True)
    t3 = engine.Join(t1, t2, 'PostId', 'PostId')
    t4 = engine.Join(t3, t1, 'AnswerId', 'PostId')
    graph = engine.ToGraph(t4, '1_2.1.UserId', '1.UserId')
    (HTHub, HTAuth) = engine.GetHits(graph)
    t5 = engine.TableFromHashMap(HTAuth, 'UserId', 'Authority')
    t5 = engine.Order(t5, ['Authority'], Asc=False)
    t5 = engine.SaveTableTSV(t5, filename2)
    return t5

engine = ringo.Ringo()
t5 = generate(engine, 'input/posts.tsv', 'input/tags.tsv', './experts.tsv')
engine.DumpTableContent(t5, 20)
engine.ShowMetadata(t5)
