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
import dateutil.parser
import datetime

if len(sys.argv) < 3:
  print """Usage: python parse_stackoverflow.py srcPostsFile srcCommentsFile dstDir [max_posts]
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
N = int(sys.argv[3]) if len(sys.argv) >= 5 else None

# Parse posts
count = 0
unicode_failures = 0
missing_info = 0
epoch = datetime.datetime(1970,1,1)
with open(srcPostsFile) as source, open(dstPostsFile, 'w') as dstPosts:
  context = etree.iterparse(source)
  for event, element in context:
    try:
      if element.tag == 'row':
        postId = element.get('Id')
        userId = element.get('OwnerUserId')
        answerId = element.get('AcceptedAnswerId')
        creationDate = int((dateutil.parser.parse(element.get('CreationDate')) - epoch).total_seconds())
        score = element.get('Score')
        if postId is None or userId is None or creationDate is None:
          missing_info += 1
          continue
        if answerId is None:
          answerId = "0"
        if score is None:
          score = "0"
        tags = element.get('Tags')
        if not tags is None:
          tags = tags[1:-1].split('><')
          if len(tags) == 0:
            dstPosts.write("\t".join((postId, userId, answerId, str(creationDate), score, "NULL")) + "\n")
          else:
            for tag in tags:
              dstPosts.write("\t".join((postId, userId, answerId, str(creationDate), score, tag)) + "\n")
        else:
            dstPosts.write("\t".join((postId, userId, answerId, str(creationDate), score, "NULL")) + "\n")
      count += 1
      if not N is None and count >= N:
        break
      if count % 10000 == 0:
        print count
    except UnicodeEncodeError:
      unicode_failures += 1
    element.clear()
print 'Parsed posts file - Rows: ' + str(count) + ', Failures: ' + str(unicode_failures) + ', Missing info: ' + str(missing_info)
