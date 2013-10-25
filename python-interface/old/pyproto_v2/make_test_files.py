import sys
import glob
import os
import xml
import elementtree.ElementTree as et
import types
import binascii
import pdb

#sizes = [10, 30, 100, 300, 1000, 3000, 10000] # Thousands of rows
sizes = [10, 50]

def create_small(srcname, destname, size):
    numrows = size*1000
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
  numrows = size * 1000
  bname, ext = os.path.splitext(fname)
  print "First pass for " + fname + " with size " + str(size) + "..."
  numcol = 0
  coldict = {}
  columns = []
  source = iter(et.iterparse(fname, events = ('start','end')))
  counter = 0
  while counter < numrows:
    try:
      event,elem = source.next()
      if event == 'end' and elem.tag == 'row':
        for name,_ in elem.attrib.items():
          name = name.encode('ascii','ignore')
          if not name in columns:
            coldict[name] = numcol
            columns.append(name)
            numcol += 1
      counter += 1
    except xml.parsers.expat.ExpatError:
      print "one warning generated"
    except StopIteration:
      break
  print "Second pass for " + fname + " with size " + str(size) + "..."
  with open(bname + "_" + str(size) + ".tsv","wb") as dest:
    string = '\t'.join(columns)+'\n'
    dest.write(string)
    source = iter(et.iterparse(fname, events = ('start','end')))
    counter = 0
    while counter < numrows:
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
        counter += 1
      except xml.parsers.expat.ExpatError:
        print "one warning generated"
      except StopIteration:
        break

def convert_file_hash(fname, size):
  numrows = size * 1000
  bname, ext = os.path.splitext(fname)
  print "First pass for " + fname + " with size " + str(size) + "..."
  numcol = 0
  coldict = {}
  columns = []
  coltypes = []
  source = iter(et.iterparse(fname, events = ('start','end')))
  counter = 0
  while counter < numrows:
    try:
      event,elem = source.next()
      if event == 'end' and elem.tag == 'row':
        for name,val in elem.attrib.items():
          if not name in columns:
            coldict[name] = numcol
            columns.append(name)
            coltypes.append(types.IntType)
            numcol += 1
          idx = coldict[name]
          if val != "":
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
  pdb.set_trace()
  print "Second pass for " + fname + " with size " + str(size) + "..."
  with open(bname + "_" + str(size) + ".hashed.tsv","wb") as dest:
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
              try:
                row[idx] = int(val)
              except ValueError:
                row[idx] = 0
            elif coltypes[idx] == types.FloatType:
              try:
                row[idx] = float(val)
              except:
                row[idx] = 0
            else: # UnicodeType
              val = val.encode('unicode-escape')
              row[idx] = binascii.crc32(val)&65535
          string = '\t'.join(map(str,row))+'\n'
          dest.write(string)
          counter += 1
      except xml.parsers.expat.ExpatError:
        print "one warning generated"
      except StopIteration:
        break

#directory = sys.argv[1]
#files = glob.glob(directory + "/*")
#files = ["/lfs/local/0/mraison/posts.xml","/lfs/local/0/mraison/comments.xml"]
files = ["/Users/martinraison/Documents/Stanford/RA/data_full/posts.xml"]
for f in files:
  base, ext = os.path.splitext(f)
  if ext == ".xml":
    for size in sizes:
      convert_file_hash(f, size)
  else:
    print "Ignoring file " + f
