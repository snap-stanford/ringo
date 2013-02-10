import table
import pdb

# select based on one condition
def select(table, attr, condition):
	return table.select(attr, condition)

def project(table, columns):
	return table.project(columns)

def group(table, attributes, aggr_attribute, aggregation_function):
	return table.group(attributes, aggr_attribute, aggregation_function)

def union(table1, table2, condition):
	result = {}
	for row in table1.getTuples(condition):
		result.add(row)

	for row in table2.getTuples(condition):
		result.add(condition)

	return result

def join(table1, table2, joinAttr1, joinAttr2, extraAttr1, extraAttr2, finalnames=None):
	# Pushed some logic in table.py to prevent messing
	# too much with row indexes outside the Table class
	#
	# finalnames allows to specify the attribute names in the final table.
	# If finalnames=None, then the default columns are:
	#     joinAttr1 + extraAttr1 + extraAttr2'
	# where extraAttr2' is a modified version of extraAttr2 that is not conflicting with extraAttr1

	# Rename columns
	assert len(joinAttr1) == len(joinAttr2)
	assert len(extraAttr1) == len(extraAttr2)
	t1 = table1.project(joinAttr1+extraAttr1)
	t2 = table2.project(joinAttr2+extraAttr2)
	newExtraAttr2 = []
	for name in extraAttr2:
		if name in extraAttr1:
			newExtraAttr2.append(name+'2')
		else:
			newExtraAttr2.append(name)
	t2 = t2.rename(joinAttr2+extraAttr2,joinAttr1+newExtraAttr2,False)
	tjoin = t1.join(t2)
	pdb.set_trace()
	if not finalnames is None:
		tjoin = tjoin.rename(tjoin.columns,finalnames,False)
	return tjoin
	#colset1 = set(table1.columns)
	#colset2 = set(table2.columns)
	#notJoined1 = colset1.difference(set(joinAttr1))
	#notJoined2 = colset2.difference(set(joinAttr2))
	#assert len(rename1) == len(tuple(notJoined1))
	#assert len(rename2) == len(tuple(notJoined2))
	## Keep columns in right order when renaming
	#oldnames1 = joinAttr1 + [name for name in table1.columns if name in notJoined1]
	#oldnames2 = joinAttr2 + [name for name in table2.columns if name in notJoined2]
	#t1 = table1.rename(oldnames1,joinAttrNames+rename1)
	#t2 = table2.rename(oldnames2,joinAttrNames+rename2)
	#return t1.join(t2)

def rename(table, oldattr, newattr):
	# Can rename several attribute names at once
	return table.rename(oldattr, newattr)

def intersect(table1, table2, condition):
	result = []
	intermediate = []
	for row in table1.getTuples(condition):
		intermediate.add(row)

	for row in table2.getTuples(condition):
		if row in intermediate:
			result.add(row)

	return result

def diff(table1, table2, condition):
	result = []
	intermediate = []
	for row in table2.getTuples(condition):
		intermediate.add(row)

	for row in table1.getTuples(condition):
		if row not in intermediate:
			result.add(row)

	return result
	