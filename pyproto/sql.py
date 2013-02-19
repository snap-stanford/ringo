import table
import pdb

# select based on one condition
def select(table, condition=[], attributes=[], newnames=None):
	t = table.select(condition)
	if len(attributes):
		t = t.project(attributes)
	if not newnames is None:
		assert len(attributes) == len(newnames)
		t.rename(attributes,newnames)
	return t

def project(table, columns):
	return table.project(columns)

def group(table, attributes, aggr_attribute=None, aggregation_function=None):
	return table.group(attributes, aggr_attribute, aggregation_function)

def order(table,attrlist,attrsort):
	return table.order(attrlist,attrsort)

def expand(table,attrlist=None):
	return table.expand(attrlist)

def union(table1, table2, condition):
	result = {}
	for row in table1.getTuples(condition):
		result.add(row)

	for row in table2.getTuples(condition):
		result.add(condition)

	return result

def join(table1, table2, joinconditions, finalnames=None):
	# finalnames allows to specify the attribute names in the final table, in the following order:
	# 1) common attributes, 2) other attributes in table 1, 3) other attributes in table 2

	# Rename columns
	joinattr1 = [attr for attr,_ in joinconditions]
	joinattr2 = [attr for _,attr in joinconditions]
	t1 = table1.copy()
	t2 = table2.copy()
	# Prevent conflicts in attribute names
	for attr1 in table1.columns:
		for attr2 in table2.columns:
			if attr1 == attr2 and not (attr1 in joinattr1 or attr2 in joinattr2):
				t1.rename(attr1,attr1+'1') # Unsafe. There could be another attribute with this name
				t2.rename(attr2,attr2+'2')
	if not isinstance(joinconditions,list):
		joinconditions = [joinconditions]
	for attr1,attr2 in joinconditions:
		t2.rename(attr2,attr1)
	tjoin = t1.join(t2)
	if not finalnames is None:
		tjoin.rename(tjoin.columns,finalnames)
	return tjoin

def rename(table, oldattr, newattr):
	# Can rename several attribute names at once
	return table.rename(oldattr, newattr, True)

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
	