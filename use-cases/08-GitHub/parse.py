'''
This module parses the json.gz files from GitHub archive and writes the tsv file for each event. The module recursively iteratores over the root directory and parses each json.gz file in the hierarchy. NOTE that it does not assume any file organization structure - all files within the root directory of type *.json.gz will be processed. 

Example:
python parse.py ~/dump
'''

import json
import sys, os
import fnmatch
import gzip
from parser.yajl_helper import *
from parser.events import *

def parse_inner(data_file, processor):
	f = None

	if data_file.index("gz")==len(data_file)-2:
		f = gzip.open(data_file, 'rb')
	else:
		f = open(data_file, 'r')

	# Create an instance of the appropriate processor
	parser = YajlParser(ContentHandler(processor))
	parser.allow_multiple_values = True
	parser.parse(f=f)
	
	f.close()

def parse(data_file):
	processor = BaseProcessor()
	
	try:
		parse_inner(data_file, processor)
	except:
		pass

	# Parse the entire file and then commit db and close connection
	processor.action()
	
def main(args):	
	if len(args)<1:
		print("Usage: python parse.py <root>")
		sys.exit(1)
	
	root = os.path.expanduser(args[0])

	for dirpath, subdirs, files in os.walk(root):
		for item in fnmatch.filter(files, "*.json.gz"):
			path = os.path.join(dirpath, item)
			parse(path)

	return 0

if __name__ == "__main__":
	main(sys.argv[1:])
