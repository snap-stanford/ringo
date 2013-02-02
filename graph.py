
class Graph:
	
	def __init__(self, name, nodes):
		self.name = name
		self.nodes = {}

	def addNode(self, nodenum, node):
		self.nodes[nodenum] = node;

	def addEdge(self, node1, node2):
		edges = self.nodes[node1];
		edges[node2] = node2;