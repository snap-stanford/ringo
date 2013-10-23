"""
 Script to parse the XML DBLP database and output a TSV file with
 schema (string Article ID, string Author)
 The DBLP dataset can be found at http://dblp.uni-trier.de/xml/
"""

from lxml import etree
import sys

if len(sys.argv) < 3:
  print "Usage: python parse.py source destination [max_articles]"
  exit(1)

srcfile = sys.argv[1]
dstfile = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) == 4 else None
count = 0
unicode_failures = 0
with open(srcfile) as source, open(dstfile, 'w') as destination:
  context = etree.iterparse(source, events=('start','end'))
  key = None
  for event, element in context:
    if event == 'start':
      try:
        if element.tag == 'article':
          key = element.get('key')
        elif element.tag == 'author':
          author = element.text
          if not key is None and not author is None:
            destination.write(key + '\t' + author + '\n')
        count += 1
        if not N is None and count >= N:
          break
        if count % 10000 == 0:
          print count
      except UnicodeEncodeError:
        unicode_failures += 1
    elif event == 'end' and element.tag == 'article':
      key = None
    element.clear()
print 'Rows: ' + str(count) + ', Failures: ' + str(unicode_failures)
