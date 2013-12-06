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
  print """Usage: python parse_stackoverflow.py srcPostsFile srcCommentsFile dstDir [max_posts]
  srcPostsFile: path to the Posts.xml file from the StackOverflow dataset
  dstDir: output directory"""
  exit(1)

srcPostsFile = sys.argv[1]
srcCommentsFile = sys.argv[2]
dstDir = sys.argv[3]
try:
  os.makedirs(dstDir)
except OSError:
  pass
dstPostsFile = os.path.join(dstDir,"posts.tsv")
dstTagsFile = os.path.join(dstDir,"tags.tsv")
dstCommentsFile = os.path.join(dstDir, "comments.tsv")
N = int(sys.argv[4]) if len(sys.argv) >= 5 else None

# Parse posts
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
        score = element.get('Score')
        if postId is None or userId is None or creationDate is None:
          missing_info += 1
          continue
        if answerId is None:
          answerId = "0"
        if score is None:
          score = "0"
        dstPosts.write("\t".join((postId, userId, answerId, creationDate, score)) + "\n")
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
print 'Parsed posts file - Rows: ' + str(count) + ', Failures: ' + str(unicode_failures) + ', Missing info: ' + str(missing_info)

"""
# Parse comments
unicode_failures = 0
missing_info = 0
with open(srcCommentsFile) as source, open(dstCommentsFile, 'w') as dstComments:
  context = etree.iterparse(source)
  for event, element in context:
    try:
      if element.tag == 'row':
        userId = element.get('UserId')
        postId = element.get('PostId')
        if postId is None or userId is None:
          missing_info += 1
          continue
        dstComments.write("\t".join((userId, postId)) + "\n")
      count += 1
      if count % 10000 == 0:
        print count
    except UnicodeEncodeError:
      unicode_failures += 1
    element.clear()
print 'Parsed comments file - Rows: ' + str(count) + ', Failures: ' + str(unicode_failures) + ', Missing info: ' + str(missing_info)
"""
