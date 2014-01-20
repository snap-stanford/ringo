'''
This module fetches the GitHub data from GitHub Archive for all events that happened between date1 and date2. Data is stored in a directory hierarchy rooted at root. The hierarchy is organized like this - root/year/month/date.gzip. The root directory must already exist.

Example:
python fetch.py -date1:2012-10-11-1 -date2:2012-10-11-2 -root:~/dump
'''

import sys
import os
from datetime import *
from subprocess import call

ROOT="-root"
DATE1="-date1"
DATE2="-date2"
DELIM=":"
FORMAT="%Y-%m-%d-%H"
BASE_URL="http://data.githubarchive.org"

data_root=""
date1 = None
date2 = None
 
def usage():
	return "Usage: python fetch.py -date1:2012-10-11-1 -date2:2012-10-11-2 -root:~/path/to/data/root"

def get_filename(date):
	filename = datetime.strftime(date, FORMAT)
	return "%s.json.gz"%filename

def fetch_file(date):
	filename = get_filename(date)
	url = "%s/%s"%(BASE_URL, filename)
	
	os.chdir(os.path.expanduser(data_root))
	path = "%s/%s/%s"%(date.year, date.month, filename)

	if not os.path.isfile(path):
		call(["curl", url, "--create-dirs","-o", path])

args = sys.argv[1:]

if len(args)<3:
	print(usage())
	sys.exit(1)

for arg in args:
	if arg.find(ROOT)==0:
		value = arg.split(DELIM)[1]
		data_root=value

	elif arg.find(DATE1)==0:
		value = arg.split(DELIM)[1]
		date1 = datetime.strptime(value, FORMAT)

	elif arg.find(DATE2)==0:
		value = arg.split(DELIM)[1]
		date2 = datetime.strptime(value, FORMAT)
	
	else:
		print(usage())
		sys.exit(1)

while date1<date2:
	print("Fetching %s"%str(date1))
	fetch_file(date1)
	date1 = date1 + timedelta(hours=1)
