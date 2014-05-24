import ringo
import sys

src_file = sys.argv[1]
Schema = [('Id','int'), ('PostTypeId','int'), ('AcceptedAnswerId','int'), ('OwnerUserId','int'), ('Body','string'), ('Tag','string')]
ringo = ringo.Ringo()
P = ringo.LoadTableTSV(Schema, src_file, '\t', True)
print ringo.GetSchema(P)
ringo.Project(P, ['Id', 'PostTypeId', 'AcceptedAnswerId', 'OwnerUserId', 'Tag'])
print ringo.GetSchema(P)
JP = ringo.Select(P, "Tag = 'java'", False)
ringo.SaveTableTSV(JP, 'jp.tsv')
#ringo.DumpTableContent(JP)
Q = ringo.Select(JP, 'PostTypeId = 1', False)
ringo.SaveTableTSV(Q, 'q.tsv')
A = ringo.Select(JP, 'PostTypeId = 2', False)
#ringo.DumpTableContent(A)
ringo.SaveTableTSV(A, 'a.tsv')
QA = ringo.Join(Q, A, 'AcceptedAnswerId', 'Id')
ringo.SaveTableTSV(QA, 'qa.tsv')
G = ringo.ToGraph(QA, 'OwnerUserId-1', 'OwnerUserId-2')
PR_MAP = ringo.PageRank(G)	# a hash map object: node/user id -> PageRank score
PR = ringo.TableFromHashMap(PR_MAP, 'user', 'score')
ringo.SaveTableTSV(PR, 'pr.tsv')
PR = ringo.Order(PR, ['score'])
ringo.SaveTableTSV(PR, 'scores.tsv')
#ringo.SaveTableBinary(PR, 'scores')
