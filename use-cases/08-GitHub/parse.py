'''
This module parses the json.gz files from GitHub archive and writes the tsv file for each event. The module recursively iteratores over the root directory and parses each json.gz file in the hierarchy. NOTE that it does not assume any file organization structure - all files within the root directory of type *.json.gz will be processed
. It creates an offset.cache file in the current directory and ignores all dates in that file - this is done to support rerun in case of intermitten failures. 

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
import calendar
import utils

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

def get_date(filename):
	sdate = filename.split(".")[0]
	return datetime.strptime(sdate, utils.CONSTANTS.FORMAT)

def main(args):	
	if len(args)<1:
		print("Usage: python parse.py <root>")
		sys.exit(1)
	
	root = os.path.expanduser(args[0])
	min_ticks = None

	if len(args)>1:
		min_ticks = int(args[1])
		print("Min Date: %s", str(datetime.fromtimestamp(int(min_ticks))))

	num_processed = 0
	FLUSH_LIMIT = 30
	writer = FileWriter()

	file_cache = []

	for dirpath, subdirs, files in os.walk(root):
		print dirpath
		for item in fnmatch.filter(files, "*.json.gz"):
			file_cache.append((dirpath, item))

	file_cache = sorted(file_cache, key= lambda tup: get_date(tup[1]))

	for file in file_cache:
		dirpath, item = file
		date = get_date(item)

		if min_ticks==None or utils.date_to_ticks(date) > min_ticks:
			path  = os.path.join(dirpath, item)
			cnt = parse(path, writer)

			print("[%s] Processed %d relevant events. Commiting changes."% (date, cnt))
			num_processed += 1

			# If FLUSH_LIMIT multiple, write to tsv files
			if num_processed % FLUSH_LIMIT == 0:
				print("Committing FileWriter")
				writer.commit()

	writer.close()
	return 0

if __name__ == "__main__":
	main(sys.argv[1:])
