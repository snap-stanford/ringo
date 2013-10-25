import table
import pdb

#Now the sql functions convert attribute names to column indexes before calling the table methods

# select based on one condition
def select(table, condition=[], attributes=[], newnames=None):
	if len(attributes):
		attrIdx = table.getIndex(attributes)
		t = table.project(attrIdx)
	t = table.select(condition)
	if not newnames is None:
		t.setNames(newnames)
	return t

def project(table, attributes):
	attrIdx = table.getIndex(attributes)
	return table.project(attrIdx)

def group(table, attributes, count=False, aggrAttr=None, aggrFunc=None):
	attrIdx = t.getIndex(attributes)
	aggrAttrIdx = t.getIndex(aggrAttr)
	return t.group(attrIdx,count,aggrAttrIdx,aggrFunc)

def join(table1, table2, joinconditions, finalnames=None):
	# finalnames allows to specify the attribute names in the final table, in the following order:
	# 1) common attributes, 2) other attributes in table 1, 3) other attributes in table 2

	# Rename columns
	t1 = table1.copy()
	t2 = table2.copy()
	joinIdx1 = t1.getIndex([attr for attr,_ in joinconditions])
	joinIdx2 = t2.getIndex([attr for _,attr in joinconditions])
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
	