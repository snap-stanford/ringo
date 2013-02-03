
class Node:
	def __init__(self, id, attributes):
		self.id = id
		self.attributes = []
		for attr in attributes:
			self.attributes.append(attr)

	def getId(self):
		return self.id

	def getAttributes(self):
		return self.attributes