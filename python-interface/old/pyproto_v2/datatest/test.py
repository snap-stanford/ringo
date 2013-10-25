import ringo
import glob
import os
import xml.parsers.expat
import elementtree.ElementTree as ET
import pdb

# 3 handler functions
def start_element(name, attrs):
    print 'Start element:', name, attrs
def end_element(name):
    print 'End element:', name
def char_data(data):
    print 'Character data:', repr(data)

p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

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
  rg.load('/lfs/local/0/mraison/posts_10000.tsv')
  rg.tables[0].name = 'posts'
  rg.start('posts','OwnerUserId')
  rg.setSource()
  rg.label('UserId1')
  rg.select('PostTypeId == 2')
  rg.link('ParentId')
  rg.join('posts','Id')
  #rg.select('PostTypeId == 1')
  rg.link('OwnerUserId')
  rg.label('UserId2')
  rg.group('Group','UserId1','UserId2')
  #rg.count('Count')
  #rg.select('Count >= 2')
  #rg.link('Group')
  rg.unique()
  rg.link('UserId2')
  rg.makegraph()
  #rg.dump()

def CommentsGraph():
  rg = ringo.Ringo()
  rg.load('data/comments.xml','data/posts.xml')
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
  rg.load('/lfs/local/0/mraison/comments_10000.tsv')
  rg.tables[0].name = 'comments'
  rg.start('comments','UserId')
  rg.setSource()
  rg.label('UserId1')
  rg.link('PostId')
  rg.join('comments','PostId')
  rg.link('UserId')
  rg.label('UserId2')
  rg.select('UserId1 != UserId2')
  rg.group('Group','UserId1','UserId2')
  #rg.count('Count')
  #rg.select('Count >= 10 && UserId1 != UserId2')
  #rg.select('Count >= 10')
  #rg.link('Group')
  rg.unique()
  rg.link('UserId2')
  rg.makegraph()
  #rg.dump()

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
  rg.load('data/badges.xml','data/posts.xml')
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
  files = glob.glob("/lfs/local/0/mraison/*")
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

def convert_files2():
  #files = glob.glob("/lfs/local/0/mraison/*")
  files = ["/lfs/local/0/mraison/a4_posthistory.xml"]
  #files = ["/lfs/local/0/mraison/a1_posts.xml"]
  for fname in files:
    bname, ext = os.path.splitext(fname)
    if ext == ".xml":
      print "First pass for " + fname + "..."
      numcol = 0
      coldict = {}
      columns = []
      source = iter(ET.iterparse(fname, events = ('start','end')))
      while 1:
        try:
          event,elem = source.next()
          if event == 'end' and elem.tag == 'row':
            for name,_ in elem.attrib.items():
              name = name.encode('unicode-escape')
              if not name in columns:
                coldict[name] = numcol
                columns.append(name)
                numcol += 1
        except xml.parsers.expat.ExpatError:
          print "one warning generated"
        except StopIteration:
          break
      print "Second pass for " + fname + "..."
      with open(bname + ".tsv","wb") as dest:
        string = '\t'.join(columns)+'\n'
        dest.write(string)
        source = iter(ET.iterparse(fname, events = ('start','end')))
        while 1:
          try:
            event,elem = source.next()
            if event == 'end' and elem.tag == 'row':
              row = [""]*numcol
              for name,val in elem.attrib.items():
                if '\t' in val:
                  print "Found guilty string"
                row[coldict[name]] = val.replace("\t","").encode('unicode-escape')
              string = '\t'.join(row)+'\n'
              dest.write(string)
          except xml.parsers.expat.ExpatError:
            print "one warning generated"
          except StopIteration:
            break

def convert_files3():
  files = ["/lfs/local/0/mraison/a4_posthistory.xml"]
  for fname in files:
    tree = ET.parse(fname)
    rows = tree.getroot()
    for row in rows:
      print row.attrib

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

def removeline(src,dest,lines):
  with open(src,'r') as sf:
    with open(dest,'w') as df:
      cnt = 1
      for line in sf:
        if not cnt in lines:
          df.write(line);
        else:
          print line
        cnt += 1



#QAGraph()
#CommentsGraph()
CommonComments()
#SameEditors()
#DatesGraph()
#BadgesGraph()
#convert_files(False)
#import_bench_tsv_fast()
#convert_files2()
#removeline("/lfs/local/0/mraison/posts_1000.tsv","/lfs/local/0/mraison/posts_1000_fix.tsv",[201873,223642,684403,701971,1126468,1147909])
