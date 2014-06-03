#
#   parse a StackOverflow posts file and print out answers in a TSV format,
#   one answer per line.
#   Output fields: (Id, PostTypeId, AcceptedAnswerId, OwnerUserId, Body)


import sys
import re
import xml.sax

limit = 11000000 # actual number of posts in posts.xml (July 2012) is 10,338,371

class StackContentHandler(xml.sax.ContentHandler):
	
	counter = 0
	fout = open('posts' + "_" + str(limit) + ".tsv","wb")
	
	def __init__(self):
		xml.sax.ContentHandler.__init__(self)
 	
 	def startElement(self, name, attrs):
		# only 'row' elements are relevant, skip elements that are not rows
		if name != "row":
			return
            
		self.counter = self.counter + 1
		if(self.counter > limit):
			raise xml.sax.SAXException('passed line limit')
			
		# extract fields
		id = str(-1)
		if attrs.has_key("Id"):
			id = attrs.getValue("Id")
		ptype = str(-1)
		if attrs.has_key("PostTypeId"):
			ptype = attrs.getValue("PostTypeId")
		aid = str(-1)
		if attrs.has_key("AcceptedAnswerId"):
			aid = attrs.getValue("AcceptedAnswerId")
		uid = str(-1)
		if attrs.has_key("OwnerUserId"):
			uid = attrs.getValue("OwnerUserId")
		body = str(-1)
		if attrs.has_key("Body"):
			body = attrs.getValue("Body")
    
		line = []
		line.append(id)
		line.append(ptype)
		line.append(aid)
		line.append(uid)
		#line.append('a') ## use this if not interested in the body text field
		post = body.replace('\r','').replace('\n','').replace('\t','')
		line.append(post.encode('ascii','ignore'))
		#line.append('a')
		record = '\t'.join(line)+'\n'
		self.fout.write(record)
		
		
 
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <file>"
        sys.exit(1)

    fname = sys.argv[1]
    f = open(fname)
    xml.sax.parse(f, StackContentHandler())
    	