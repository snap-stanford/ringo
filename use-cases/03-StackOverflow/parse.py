"""
 Script to parse the XML StackOverflow database and output a TSV file with
 schema (string Key, string Author)
 The DBLP dataset can be found at http://dblp.uni-trier.de/xml/
"""

from lxml import etree
import sys
import os

if len(sys.argv) < 3:
  print """Usage: python parse.py sourcedir destination [max_items]
  source: input StackOverflow directory containing .xml files
  destination: output directory"""
  exit(1)

def parseFile(srcFile, destFile, attributes, N = None):
  print 'Parsing file %s' % srcFile
  count = 0
  unicode_failures = 0
  with open(srcFile) as source, open(destFile, 'w') as destination:
    context = etree.iterparse(source)
    for event, element in context:
      try:
        if element.tag == 'row':
          row = (element.get(attr) for attr in attributes)
          row = (x if not x is None else "0" for x in row)
          destination.write("\t".join(row) + "\n")
        count += 1
        if not N is None and count >= N:
          break
        if count % 10000 == 0:
          print count
      except UnicodeEncodeError:
        unicode_failures += 1
      element.clear()
  print 'Rows: ' + str(count) + ', Failures: ' + str(unicode_failures)

srcPostsFile = os.path.join(sys.argv[1],"posts.xml")
srcCommentsFile = os.path.join(sys.argv[1],"comments.xml")
dstPostsFile = os.path.join(sys.argv[2],"posts.tsv")
dstCommentsFile = os.path.join(sys.argv[2],"comments.tsv")
N = int(sys.argv[3]) if len(sys.argv) == 4 else None
parseFile(srcPostsFile, dstPostsFile, ('Id', 'ParentId', 'OwnerUserId', 'Score', 'Tags'), N)
parseFile(srcCommentsFile, dstCommentsFile, ('UserId', 'PostId'), N)
