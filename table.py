
class Table:

	def __init__(self, name):
		self.name = name
		self.attributes = []
		self.data = []

	def set_attributes(self, attributes):
		for attr in attributes:
			self.attributes.append(attr)

	def load(self, filename):
		f = open(filename, 'r')
		for line in f:
			row = []
			values = line.split('\t')
			for v in values:
				row.append(v)
			self.data.append(row)

	def name(self):
		return self.name

	def ithrow(self, data, i):
		return data[i]

	def columnbyattr(self, data, attr):
		result = {}
		for row in data:
			result.add(row[attr])

		return result