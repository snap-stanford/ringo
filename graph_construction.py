import table

def select(table, condition):
	result = table.getTuples(condition)
	return result

def project(table, columns):
	result = table.getColumns(columns)
	return result

def group(table, attributes, aggregation_attributes, aggregation_function):
	result = {}

	for row in table:
		for attr in aggregation_attributes:
			aggregation_function(row)

	return result

def union(table1, table2, condition):
	result = {}
	for row in table1:
		if row.condition == condition:
			result.add(row)

	for row in table2:
		if row.condition == condition:
			result.add(condition)

	return result

def join(table1, table2, condition):

def rename:

def intersect:

def diff:

def makeGraph(table1, table2, table3):
	