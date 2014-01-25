'''
Utilities for the GitHub use
'''
import calendar
import datetime
import dateutil.parser

class CONSTANTS:
	FORMAT="%Y-%m-%d-%H"

# Converts string representation of date time in ISO format to 
def date_to_ticks(date):
	obj = dateutil.parser.parse(date)
	return calendar.timegm(obj.utctimetuple())
