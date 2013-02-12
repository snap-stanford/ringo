import table
import pdb

# select based on one condition
def select(table, attr, condition):
	return table.select(attr, condition)

def project(table, columns):
	return table.project(columns)

def group(table, attributes, aggr_attribute=None, aggregation_function=None):
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
	if not finalnames is None:
		tjoin = tjoin.rename(tjoin.columns,finalnames,False)
	return tjoin

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
	