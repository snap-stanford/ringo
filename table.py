
class Table:
	
	def __init__(self, name, data):
		self.name = name
		self.data = {}
		self.__update_data(data);

	def update_data(self, data):
		for row in data:
			self.data.add(row)

	def name(self):
		return self.name

	def ithrow(self, data, i):
		return data[i]

	def columnbyattr(self, data, attr):
		result = {}
		for row in data:
			result.add(row[attr])

		return result