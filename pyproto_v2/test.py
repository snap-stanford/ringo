import ringo

r = ringo.Ringo()
r.load('data/comments.xml')
t = r.tables[0]
#r.wtable = t
#r.select('UserId >= 15')
r.setWorkingTable('comments')
r.setWorkingColumn('UserId')
#r.join('comments','UserId')
#r.group('Group','PostId','Score')
#r.dump(100)
#r.order('Order','UserId','PostId')
#r.count('Count','UserId','PostId')
#r.next('UserId','CreationDate','NextId')
#r.unique('UserId','PostId')
r.setSourceContext()
r.link('PostId')
r.makegraph()