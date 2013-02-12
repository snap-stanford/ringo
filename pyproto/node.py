
class Node:
	def __init__(self, id, attributes):
		self.id = id
		self.attributes = {}
		for attr, value in attributes.iteritems():
			self.attributes[attr] = value

	def getId(self):
		return self.id

	def getAttributes(self):
		return self.attributes