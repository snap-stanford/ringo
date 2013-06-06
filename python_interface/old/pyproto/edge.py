
class Edge:
	def __init__(self, dest, attributes):
		self.id = id
		self.dest = dest
		self.attributes = {}
		for attr, value in attributes.iteritems():
			self.attributes[attr] = value

	def getId(self):
		return self

	def getDest(self):
		return self.dest

	def getAttributes(self):
		return self.attributes
