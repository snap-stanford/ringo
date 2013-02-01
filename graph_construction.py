
def select(table, attributes, condition):
	result = {}

	for row in table:
		if row.condition == condition:
			result.add(row)

	return result

def project(table, attributes, condition):
	result = {}

	for col in table:
		if col.condition == condition:
			result.add(row)

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
