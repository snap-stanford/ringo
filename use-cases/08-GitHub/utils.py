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

def rows(table, maxRows):
	S = table.GetSchema()
	line = ""
	names = []
	types = []
	for i, attr in enumerate(S):
		names.append(attr.GetVal1())
		types.append(attr.GetVal2())

	RI = table.BegRI()
	cnt = 0

	while RI < table.EndRI() and (maxRows is None or cnt < maxRows):
		elements = []

		for c,t in zip(names,types):
			if t == 0: # int
				elements.append(str(RI.GetIntAttr(c)))
			elif t == 1: # float
				elements.append("{0:.6f}".format(RI.GetFltAttr(c)))
			elif t == 2: # string
				elements.append(RI.GetStrAttr(c))
			else:
				raise NotImplementedError("unsupported column type")
	
		cnt += 1
		yield elements
		RI.Next()

