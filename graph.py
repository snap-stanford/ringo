
class Graph:

	def __init__(self, name, nodes):
		self.name = name
		self.nodes = {}
		for id, node in nodes.iteritems():
			self.nodes[id] = node


	def addNode(self, node):
		self.nodes[node.getId()] = node;

	def addEdge(self, edge):
		edges = self.nodes[edge.getNode1().getId()];
		edges[edge.getNode2().getId()] = attributes;

