import table

def select(table, condition):
	result = table.getTuples(condition)
	return result

def project(table, columns):
	result = table.getColumns(columns)
	return result

# group by merchant then by customer
def group(table, attributes, aggr_attribute, aggregation_function):
	result = table.aggregate(attributes, aggr_attribute, aggregation_function)
	return result

def union(table1, table2, condition):
	result = {}
	for row in table1.getTuples(condition):
		result.add(row)

	for row in table2.getTuples(condition):
		result.add(condition)

	return result

def join(table1, table2):
	result = []

	commonCols = intersect(table1.getColumns(), table2.getColumns())
	for row in table1:
		newrow = []
		for row2 in table2:
			for col in commonCols:
				valid = 1
				if table1.getElem(row1, col) != table2.getElem(row, col):
					valid = 0
				if valid == 1:

				for elem in row1:
					newrow.append(elem)
				for col in table2.getColumns():
					if col not in commonCols:
						newrow.append(table2.getElem(row2, col))

		if len(newrow) > 0:
			result.append(newrow)

	return result

def rename(table, oldattr, newattr):
	table.setAttrName(oldattr, newattr)

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
	