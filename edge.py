
class Edge:
	def __init__(self, id, nodeid1, nodeid2, attributes):
		self.id = id
		self.nodeid1 = nodeid1
		self.nodeid2 = nodeid2
		self.attributes = {}
		for attr, value in attributes.iteritems():
			self.attributes[attr] = value

	def getId(self):
		return self

	def getNodeid1(self):
		return self.nodeid1

	def getNodeid2(self):
		return self.nodeid2

	def getAttributes(self):
		return self.attributes
