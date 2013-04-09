import ringo
import pdb
import table
import time
import glob
import os

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
  start = time.clock()
  rg = ringo.Ringo()
  rg.load('data/posts.xml')
  rg.setSource('posts','OwnerUserId')
  #rg.setWorkingTable('posts')
  #rg.setWorkingColumn('OwnerUserId')
  rg.label('UserId1')
  rg.select('PostTypeId == 2')
  #rg.setSourceContext()
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
  start = time.clock()
  rg = ringo.Ringo()
  rg.load('data/comments.xml','data/posts.xml')
  rg.setSource('comments','UserId')
  rg.label('UserId1')
  rg.link('PostId')
  rg.join('posts','Id')
  rg.link('OwnerUserId')
  rg.label('UserId2')
  rg.makegraph()
  rg.dump(30,30)

def CommonComments():
  rg = ringo.Ringo()
  rg.load('data/comments.xml')
  rg.setSource('comments','UserId')
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
  rg.dump(30,30)

######## DATAFILE NOT AVAILABLE FOR THE MOMENT #######
########     (missing UserId for each vote)    #######
def CommonVoters():
  rg = ringo.Ringo()
  rg.load('data/votes.xml')
  rg.setSource('votes','UserId')
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
  rg.dump(30,30)

def SameEditors():
  start = time.clock()
  rg = ringo.Ringo()
  rg.load('data/posthistory.xml')
  rg.setSource('posthistory','PostId')
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
  rg.dump(30,30)

def Dates():
  start = time.clock()
  rg = ringo.Ringo()
  rg.load('data/posthistory.xml')
  rg.setSource('posthistory','PostId')
  rg.group('FullEdits','CreationDate','PostId')
  rg.unique() # If a user changes different elements (eg, body, title and tags),
              # then there is one row for each element. These two lines group them into one.
  rg.order('Order','UserId','CreationDate')
  rg.group('Group','UserId')
  rg.link('PostId')
  rg.next('Group','Order','NextPostId')
  rg.makegraph()
  rg.dump(30,30)

def BadgesGraph():
  start = time.clock()
  rg = ringo.Ringo()
  rg.load('data/badges.xml','data/posts.xml')
  rg.setSource('badges','Name')
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
  rg.dump(30,30)

def convert_files():
  files = glob.glob("../../data_full/*.xml")
  for f in files:
    name, ext = os.path.splitext(f)
    if ext == ".xml":
      rg = ringo.Ringo()
      print 'Importing file ' + f + '...'
      rg.load(f)
      print "Writing .tsv file for " + f + "..."
      rg.tables[0].write_tsv(name + ".tsv")

def import_bench_xml():
  import_bench_ext("xml")

def import_bench_tsv():
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
#Dates()
#BadgesGraph()
#import_bench_tsv()