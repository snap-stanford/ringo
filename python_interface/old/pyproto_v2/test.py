import ringo
import glob
import os

# GRAPH CREATION:
# start(table,column)
# ...transformation...
# setSource() (source nodes are in working column)
# ...transformation...
# makeGraph (destination nodes are in the working column, add those who don't exist already)

# TODO: bipartite graphs? Here we only have one kind of nodes (this is how the underlying C++ graph structure works anyway)

#### SAMPLE GRAPHS ####
def QAGraph():
  rg = ringo.Ringo()
  rg.load('data/posts.tsv')
  rg.start('posts','OwnerUserId')
  rg.setSource()
  rg.label('UserId1')
  rg.select('PostTypeId == 2')
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

def CommentsGraph():
  rg = ringo.Ringo()
  rg.load('data/comments.xml')
  rg.load('data/posts.xml')
  rg.start('comments','UserId')
  rg.setSource()
  rg.label('UserId1')
  rg.link('PostId')
  rg.join('posts','Id')
  rg.link('OwnerUserId')
  rg.label('UserId2')
  rg.makegraph()
  rg.dump()

def CommonComments():
  rg = ringo.Ringo()
  rg.load('data/comments.xml')
  rg.start('comments','UserId')
  rg.setSource()
  rg.label('UserId1')
  rg.link('PostId')
  rg.join('comments','PostId')
  rg.link('UserId')
  rg.label('UserId2')
  rg.group('Group','UserId1','UserId2')
  rg.count('Count')
  #rg.select('Count >= 10 && UserId1 != UserId2')
  rg.select('Count >= 10')
  rg.link('Group')
  rg.unique()
  rg.link('UserId2')
  rg.makegraph()
  rg.dump()

######## DATAFILE NOT AVAILABLE FOR THE MOMENT #######
########     (missing UserId for each vote)    #######
def CommonVoters():
  rg = ringo.Ringo()
  rg.load('data/votes.xml')
  rg.start('votes','UserId')
  rg.setSource()
  rg.label('UserId1')
  rg.link('PostId')
  rg.join('votes','PostId')
  rg.link('UserId')
  rg.label('UserId2')
  rg.select('UserId1 != UserId2')
  rg.group('Group','UserId1','UserId2')
  rg.count('Count')
  rg.select('Count >= 10')
  rg.link('Group')
  rg.unique()
  rg.link('UserId2')
  rg.makegraph()
  rg.dump()

def SameEditors():
  rg = ringo.Ringo()
  rg.load('data/posthistory.xml')
  rg.start('posthistory','PostId')
  rg.setSource()
  rg.label('PostId1')
  rg.link('UserId')
  rg.join('posthistory','UserId')
  rg.link('PostId')
  rg.label('PostId2')
  rg.select('PostId1 != PostId2')
  rg.group('Group','PostId1','PostId2')
  rg.unique()
  rg.link('PostId2')
  rg.makegraph()
  rg.dump()

def DatesGraph():
  rg = ringo.Ringo()
  rg.load('data/posthistory.xml')
  rg.start('posthistory','PostId')
  rg.setSource()
  rg.group('FullEdits','CreationDate','PostId')
  rg.unique() # If a user changes different elements (eg, body, title and tags),
              # then there is one row for each element. These two lines group them into one.
  rg.order('Order','UserId','CreationDate')
  rg.group('Group','UserId')
  rg.link('PostId')
  rg.next('Group','Order','NextPostId')
  rg.makegraph()
  rg.dump()

def BadgesGraph():
  rg = ringo.Ringo()
  rg.load('data/badges.xml')
  rg.load('data/posts.xml')
  rg.start('badges','Name')
  rg.setSource()
  rg.label('Badge1')
  rg.link('UserId')
  rg.join('posts','OwnerUserId')
  rg.select('PostTypeId == 2')
  rg.link('ParentId')
  rg.join('posts','Id')
  rg.select('PostTypeId == 1')
  rg.link('OwnerUserId')
  rg.join('badges','UserId')
  rg.link('Name')
  rg.label('Badge2')
  rg.group('Group','Badge1','Badge2')
  rg.count('Count')
  rg.select('Count >= 100')
  rg.link('Group')
  rg.unique()
  rg.link('Badge2')
  rg.makegraph()
  rg.dump()

def convert_files(safe = False):
  files = glob.glob("../../data_full/*")
  for f in files:
    name, ext = os.path.splitext(f)
    if ext == ".xml":
      rg = ringo.Ringo()
      print 'Importing file ' + f + '...'
      rg.load(f)
      print "Writing file for " + f + "..."
      if safe:
        rg.tables[0].write_tsv(name + ".tsvs")
      else:
        rg.tables[0].write_tsv_fast(name + ".tsv")

def import_bench_xml():
  import_bench_ext("xml")

def import_bench_tsv():
  import_bench_ext("tsvs")

def import_bench_tsv_fast():
  import_bench_ext("tsv")

def import_bench_ext(ext):
  files = glob.glob("../../data_full/*." + ext)
  for f in files:
    print 'Importing file ' + f + '...'
    rg = ringo.Ringo()
    rg.load(f)
    print str(os.path.getsize(f)) + ' bytes, ' + str(rg.tables[0].numrows()) + ' rows'
    #print 'Setting up source... (i.e. copying initial table)'
    #rg.setSource(rg.tables[0].name,iter(rg.tables[0].cols[0]).next())



QAGraph()
#CommentsGraph()
#CommonComments()
#SameEditors()
#DatesGraph()
#BadgesGraph()
#convert_files(True)
#import_bench_tsv_fast()