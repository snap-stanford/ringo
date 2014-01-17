import sys
import json
from yajl import *

# Content handler constructs a valid top-level JSON object and calls the processor method to handle the object
class ContentHandler(YajlContentHandler):
   	def __init__(self, processor):
		self.js = ""    
		self.stack = []
		self.processor = processor    	
	def yajl_null(self, ctx):
    		self.js += "null,"
	
	def yajl_boolean(self, ctx, boolVal):
		self.js += ('true' if boolVal else 'false') + ","
    	
	def yajl_integer(self, ctx, integerVal):
		self.js += integerVal + ","
    	
	def yajl_double(self, ctx, doubleVal):
		self.js += doubleVal + ","
    
	def yajl_number(self, ctx, stringNum):
        	''' Since this is defined both integer and double callbacks are useless '''
        	num = float(stringNum) if '.' in stringNum else int(stringNum)
    		self.js+=str(num) + ","
    
	def yajl_string(self, ctx, stringVal):
		s = self.escape(stringVal)
    		self.js +=  ("%s,")%s
    
	def yajl_map_key(self, ctx, stringVal):
		self.js+= ("\"%s\":")%stringVal
    	
	def yajl_start_array(self, ctx):
		self.js+='['
    	
	def yajl_end_array(self, ctx):
		self.prune()
        	self.js+='],'
    
	def yajl_start_map(self, ctx):
      		self.stack.append("{") 
    		self.js+='{'
    
	def yajl_end_map(self, ctx):
		self.stack.pop()	

		if len(self.stack)==0:
			# Remove extraneous ',' if present
			# This is required for both inner and outmost JSON objects
			self.prune()
			self.js += "}"
			self.processor.process(self.js)
			self.js = ""
		else:
			# Remove extraneous ',' if present. 
			# This is required for each inner JSON object as well
			self.prune()
			self.js += "},"

	def prune(self):
		if self.js[-1] == ",":
			self.js = self.js[:-1]

	def escape(self, s):
		return json.dumps(s)
