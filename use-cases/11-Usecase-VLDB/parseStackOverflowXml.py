import sys
import glob
import os
import xml
import xml.etree.ElementTree as et
import types

sizes = [1000000] # StackOverflow dataset has 15,838,934 posts

def create_small(srcname, destname, size):
    numrows = size
    with open(srcname,"r") as src:
        with open(destname, "w") as dest:
            dest.write(src.next()) # Write xml header
            name = src.next()[1:-3]
            dest.write("<" + name + ">")
            cnt = 0
            for line in src:
                if cnt > numrows:
                    break;
                dest.write(line)
                cnt += 1
            if cnt > numrows:
                dest.write("</" + name + ">")

def convert_file(fname, size):
  numrows = size
  bname, ext = os.path.splitext(fname)
  print "First pass for " + fname + " with size " + str(size) + "..."
  numcol = 0
  coldict = {}
  columns = []
  coldata = []
  colcounts = []
  coltypes = []
  source = iter(et.iterparse(fname, events = ('start','end')))
  counter = 0
  while counter < numrows:
    try:
      event,elem = source.next()
      if event == 'end' and elem.tag == 'row':
        for name,val in elem.attrib.items():
          name = name.encode('unicode-escape')
          if not name in columns:
            coldict[name] = numcol
            columns.append(name)
            coldata.append({})
            colcounts.append(0)
            coltypes.append(types.IntType)
            numcol += 1
          idx = coldict[name]
          if coltypes[idx] == types.IntType:
            try:
              int(val)
            except ValueError:
              coltypes[idx] = types.FloatType
          if coltypes[idx] == types.FloatType:
            try:
              float(val)
            except ValueError:
              coltypes[idx] = types.UnicodeType
        counter += 1
    except xml.parsers.expat.ExpatError:
      print "one warning generated"
    except StopIteration:
      break
  print "Second pass for " + fname + " with size " + str(size) + "..."
  with open(bname + "_" + str(size) + ".test.tsv","wb") as dest:
    string = '\t'.join(columns)+'\n'
    dest.write(string)
    source = iter(et.iterparse(fname, events = ('start','end')))
    counter = 0
    while counter < numrows:
      try:
        event,elem = source.next()
        if event == 'end' and elem.tag == 'row':
          row = [-1]*numcol
          for name,val in elem.attrib.items():
            idx = coldict[name]
            if coltypes[idx] == types.IntType:
              row[idx] = int(val)
            elif coltypes[idx] == types.FloatType:
              row[idx] = float(val)
            else: # UnicodeType
              if not val in coldata[idx]:
              	row[idx] = 'a'
                #coldata[idx][val] = colcounts[idx]
                #colcounts[idx] += 1
              #row[idx] = coldata[idx][val]
          string = '\t'.join(map(str,row))+'\n'
          dest.write(string)
          counter += 1
      except xml.parsers.expat.ExpatError:
        print "one warning generated"
      except StopIteration:
        break
    print str(counter) + "rows written to file."
    	
#directory = sys.argv[1]
#files = glob.glob(directory + "/*")
#files = ["/lfs/local/0/yonathan/posts.xml"] 
files = ["/dfs/ilfs2/0/ringo/StackOverflow_VLDB/posts.xml"] 

for f in files:
  base, ext = os.path.splitext(f)
  if ext == ".xml":
    for size in sizes:
      convert_file(f, size)
  else:
    print "Ignoring file " + f
