import sys
import ringo

posts_file = sys.argv[1]
tags_file = sys.argv[2]
ringo = ringo.Ringo()
S_posts = [('Id','int'), ('PostTypeId','int'), ('AcceptedAnswerId','int'), ('OwnerUserId','int'), ('Body','string')]
S_tags = [('Id','int'), ('Tag','string')]

posts = ringo.LoadTableTSV(S_posts, posts_file)
#print ringo.ringo.DumpTableContent(posts) # buggy...
q_tags = ringo.LoadTableTSV(S_tags, tags_file)
QT = ringo.Join(posts, q_tags, "Id", "Id")
QT = ringo.Project(QT, ['Id', 'PostTypeId', 'AcceptedAnswerId', 'OwnerUserId', 'Body', 'Tag'])
a_tags = ringo.Project(QT, ['AcceptedAnswerId', 'Tag'], False)
AT = ringo.Join(posts, a_tags, 'Id', 'AcceptedAnswerId')
AT = ringo.Project(AT, ['Id', 'PostTypeId', 'AcceptedAnswerId', 'OwnerUserId', 'Body', 'Tag'])
T = ringo.UnionAll(QT, AT)
ringo.SaveTableTSV(T, 'so_posts.tsv')
