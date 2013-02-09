import table

# select based on one condition
def select(table, attr, condition):
	return table.getTuples(condition, attr)

def project(table, columns):
	return table.getColumns(columns)

def group(table, attributes, aggr_attribute, aggregation_function):
	return table.aggregate(attributes, aggr_attribute, aggregation_function)

def union(table1, table2, condition):
	result = {}
	for row in table1.getTuples(condition):
		result.add(row)

	for row in table2.getTuples(condition):
		result.add(condition)

	return result

def join(table1, table2, common=[]):
	# Pushed the logic in table.py to prevent messing
	# too much with row indexes outside the Table class
	return table1.join(table2,common)

def rename(table, oldattr, newattr):
	# Can rename several attribute names at once
	table.rename(oldattr, newattr)

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
	