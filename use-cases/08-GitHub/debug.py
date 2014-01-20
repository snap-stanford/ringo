import json
import sys
from parser.yajl_helper import *
from parser.events import *
from parse import parse_inner

# Returns the deserialized JSON objects of interests

def main(args):
	data_file = args[0]
	event = args[1]
	cnt = 1

	if len(args)>3:
		cnt = int(args[2])

	# Create an instance of the appropriate processor
	processor = DebugProcessor(event, cnt)
	parse_inner(data_file, processor)
	return 0

if __name__ == "__main__":
	if len(sys.argv)<2:
		print("Usage: python program <data_file> <event>")

	main(sys.argv[1:])

