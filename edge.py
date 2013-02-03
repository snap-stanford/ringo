
class Edge:
	def __init__(self, id, node1, node2, attributes):
		self.id = id
		self.node1 = node1
		self.node2 = node2
		self.attributes = []
		for attr in attributes:
			self.attributes.append(attr)

	def getId(self):
		return self

	def getNode1(self):
		return self.node1

	def getNode2(self):
		return self.node2

	def getAttributes(self):
		return self.attributes
