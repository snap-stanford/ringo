import ringo
import pdb

#### SIMPLE FUNCTIONALITY TESTING ####
#r = ringo.Ringo()
#r.load('data/comments.xml')
#t = r.tables[0]
#r.wtable = t
#r.select('UserId >= 15')
#r.setWorkingTable('comments')
#r.setWorkingColumn('UserId')
#r.join('comments','UserId')
#r.group('Group','PostId','Score')
#r.dump(100)
#r.order('Order','UserId','PostId')
#r.count('Count','UserId','PostId')
#r.next('UserId','CreationDate','NextId')
#r.unique('UserId','PostId')
#r.setSourceContext()
#r.link('PostId')
#r.makegraph()

#### SAMPLE GRAPHS ####
def QAGraph():
  rg = ringo.Ringo()
  rg.load('data/posts.xml')
  rg.setWorkingTable('posts')
  rg.setWorkingColumn('OwnerUserId')
  rg.label('UserId1')
  rg.select('PostTypeId == 2')
  rg.setSourceContext()
  rg.link('ParentId')
  rg.join('posts','Id')
  rg.select('PostTypeId == 1')
  rg.link('OwnerUserId')
  rg.label('UserId2')
  rg.group('Group','UserId1','UserId2')
  rg.count('Count')
  rg.select('Count >= 2')
  rg.link('Group')
  rg.unique()
  rg.link('UserId2')
  rg.makegraph()
  rg.dump()

QAGraph()