import ringo
import sys

src_file = sys.argv[1]
Schema = [('Id','int'), ('PostTypeId','int'), ('AcceptedAnswerId','int'), ('OwnerUserId','int'), ('Body','string'), ('Tag','string')]
ringo = ringo.Ringo()
P = ringo.LoadTableTSV(Schema, src_file, '\t', True)
ringo.Project(P, ['Id', 'PostTypeId', 'AcceptedAnswerId', 'OwnerUserId', 'Tag'])

JP = ringo.Select(P, "Tag = 'java'", False)
Q = ringo.Select(JP, 'PostTypeId = 1', False)
A = ringo.Select(JP, 'PostTypeId = 2', False)

QA = ringo.Join(Q, A, 'AcceptedAnswerId', 'Id')
G = ringo.ToGraph(QA, 'OwnerUserId-1', 'OwnerUserId-2')
PR_MAP = ringo.PageRank(G)	# a hash map object: node/user id -> PageRank score
PR = ringo.TableFromHashMap(PR_MAP, 'user', 'score')
PR = ringo.Order(PR, ['score'])
ringo.SaveTableTSV(PR, 'scores.tsv')
#ringo.SaveTableBinary(PR, 'scores')
ringo.GenerateProvenance(G, 'G.py')
