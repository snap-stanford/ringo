"""
 Script to parse the XML StackOverflow database and output the following
 database in TSV format:
    posts(PostId, OwnerUserId, AcceptedAnswerId)
    tags(PostId, Tags)
 The DBLP dataset can be found at http://dblp.uni-trier.de/xml/
"""

from lxml import etree
import sys
import os

if len(sys.argv) < 3:
  print """Usage: python parse.py srcPostsFile dstDir [max_items]
  srcPostsFile: path to the Posts.xml file from the StackOverflow dataset
  dstDir: output directory"""
  exit(1)

srcPostsFile = sys.argv[1]
dstDir = sys.argv[2]
try:
  os.makedirs(dstDir)
except OSError:
  pass
dstPostsFile = os.path.join(dstDir,"posts.tsv")
dstTagsFile = os.path.join(dstDir,"tags.tsv")
N = int(sys.argv[3]) if len(sys.argv) >= 4 else None
count = 0
unicode_failures = 0
missing_info = 0
with open(srcPostsFile) as source, open(dstPostsFile, 'w') as dstPosts, open(dstTagsFile, 'w') as dstTags:
  context = etree.iterparse(source)
  for event, element in context:
    try:
      if element.tag == 'row':
        postId = element.get('Id')
        userId = element.get('OwnerUserId')
        answerId = element.get('AcceptedAnswerId')
        creationDate = element.get('CreationDate')
        if postId is None or userId is None or creationDate is None:
          missing_info += 1
          continue
        if answerId is None:
          answerId = "0"
        dstPosts.write("\t".join((postId, userId, answerId, creationDate)) + "\n")
        tags = element.get('Tags')
        if not tags is None:
          tags = tags[1:-1].split('><')
          for tag in tags:
            dstTags.write("\t".join((postId, tag)) + "\n")
      count += 1
      if not N is None and count >= N:
        break
      if count % 10000 == 0:
        print count
    except UnicodeEncodeError:
      unicode_failures += 1
    element.clear()
print 'Rows: ' + str(count) + ', Failures: ' + str(unicode_failures) + ', Missing info: ' + str(missing_info)
