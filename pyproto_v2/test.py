import ringo

r = ringo.Ringo()
r.load('data/comments.xml')
t = r.tables[0]
#r.wtable = t
#r.select('UserId >= 15')
r.setWorkingTable('comments')
r.setWorkingColumn('UserId')
r.join('comments','UserId')