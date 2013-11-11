"""
 Script to parse the XML DBLP database and output a TSV file with
 schema (string Key, string Author)
 The DBLP dataset can be found at http://dblp.uni-trier.de/xml/
"""

from lxml import etree
import sys
import os

if len(sys.argv) < 3:
  print """Usage: python parse.py source destination [max_articles]
  source: input DBLP .xml file
  destination: name of the output directory"""
  exit(1)

AUTHORS_FILE_NAME = 'authors.tsv'
YEAR_FILE_NAME = 'year.tsv'

srcFile = sys.argv[1]
dstDir = sys.argv[2]
if not dstDir is None:
  try:
    os.makedirs(dstDir)
  except OSError:
    pass
N = int(sys.argv[3]) if len(sys.argv) == 4 else None
count = 0
unicode_failures = 0
with open(srcFile) as source, \
     open(os.path.join(dstDir, AUTHORS_FILE_NAME), 'w') as authorsFile, \
     open(os.path.join(dstDir, YEAR_FILE_NAME), 'w') as yearFile:
  context = etree.iterparse(source, events=('start','end'))
  key = None
  authors = []
  year = None
  for event, element in context:
    if event == 'start':
      try:
        if element.tag == 'article':
          key = element.get('key')
        elif element.tag == 'author':
          authors.append(etree.tostring(element, encoding='UTF-8', method="text").strip())
        elif element.tag == 'year':
          year = element.text
        count += 1
        if not N is None and count >= N:
          break
        if count % 10000 == 0:
          print count
      except UnicodeEncodeError:
        unicode_failures += 1
    elif event == 'end' and element.tag == 'article':
      if not key is None:
        for author in authors:
          authorsFile.write(key + '\t' + author + '\n')
        if not year is None:
          yearFile.write(key + '\t' + year + '\n')
      key = None
      authors = []
      year = None
    element.clear()
print 'Rows: ' + str(count) + ', Failures: ' + str(unicode_failures)
