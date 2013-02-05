import table

def select(table, condition):
	result = table.getTuples(condition)
	return result

def project(table, columns):
	result = table.getColumns(columns)
	return result

def group(table, attributes, aggregation_attributes, aggregation_function):
	result = []

	for row in table:
		for attr in aggregation_attributes:
			result.append(table.aggregate(aggregation_function, attr))

	return result

def union(table1, table2, condition):
	result = {}
	for row in table1.getTuples(condition):
		result.add(row)

	for row in table2.getTuples(condition):
		result.add(condition)

	return result

def join(table1, table2, col):
	result = []
	for row in table1:
		newrow = []
		for row2 in table2:
			if (row1[col] == row2[col]):
				for elem in row1:
					newrow.append(elem)
				for elem in row2:
					if elem != row2[col]:
						newrow.append(elem)
		if len(newrow) > 0:
			result.append(newrow)

	return result

def rename(table, oldattr, newattr):
	table.setAttr(oldattr, newattr)

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
	for row in table1.getTuples(condition):
		intermediate.add(row)

	for row in table2.getTuples(condition):
		if row not in intermediate:
			result.add(row)

	return result

def makeGraph(table1, table2, table3):
	