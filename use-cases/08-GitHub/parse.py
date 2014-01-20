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
from datetime import *

def parse_inner(data_file, processor):
	f = None

	if data_file.index("gz")==len(data_file)-2:
		f = gzip.open(data_file, 'rb')
	else:
		f = open(data_file, 'r')

	# Create an instance of the appropriate processor
	parser = yajl.YajlParser(ContentHandler(processor))
	parser.allow_multiple_values = True
	parser.parse(f=f)
	f.close()

	# Parse the entire file and then commit db and close connection
 	return processor.action()

def parse(data_file, writer):
	processor = BaseProcessor(writer)
	
	try:
		cnt = parse_inner(data_file, processor)
		return cnt
	except:
		print(sys.exc_info())
	
	return 0

CACHE_FILE="offset.cache"
FORMAT="%Y-%m-%d-%H"

def get_date(filename):
	sdate = filename.split(".")[0]
	return datetime.strptime(sdate, FORMAT)

def main(args):	
	if len(args)<1:
		print("Usage: python parse.py <root>")
		sys.exit(1)
	
	root = os.path.expanduser(args[0])
	date_cache = {}
		
	f = open(CACHE_FILE, "a+")

	try:
		for line in f.readlines():
			date_cache[datetime.strptime(line, FORMAT)] = 0
	except:
		print("Invalid Date")
		print(sys.exc_info())
	
	num_processed = 0
	FLUSH_LIMIT = 30
	writer = FileWriter()

	for dirpath, subdirs, files in os.walk(root):
		for item in fnmatch.filter(files, "*.json.gz"):
			date = get_date(item)	

			if date not in date_cache:
				path = os.path.join(dirpath, item)
				cnt = parse(path, writer)

				#cnt = 0
				print("[%s] Processed %d relevant events. Commiting changes."% (date, cnt))
				num_processed += 1

				# If FLUSH_LIMIT multiple, write to tsv files
				if num_processed % FLUSH_LIMIT == 0:
					print("Committing FileWriter")
					writer.commit()

				# Update date cache
				f.write(datetime.strftime(date, FORMAT) + "\n")
				f.flush()
			else:
				print("Skipping %s due to cache" % date)

	writer.close()
	f.close()
	return 0

if __name__ == "__main__":
	main(sys.argv[1:])
