
class Graph:

	def __init__(self, name, nodes, graphType):
		self.name = name
		self.nodes = {}
		for id, node in nodes.iteritems():
			self.nodes[id] = node

	def addNode(self, node):
		self.nodes[node.getId()] = node;

	def addEdge(self, node1, edge):
		edges = self.nodes[node1];
		edges[edge.getDest()] = attributes;

