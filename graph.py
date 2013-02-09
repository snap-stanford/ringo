
class Graph:

	# self.nodes: dictionary of nodes {NodeId:Attributes}
	# self.edges: stores edges with adjacency list:
	#			{NodeId:{OutEdges}}, OutEdges={DestNodeId:EdgeAttributes}

	def __init__(self, name, graphType):
		self.name = name
		self.nodes = {} # dictionary {NodeId:Attributes}
		self.edges = {} # dictionary {EdgeId:Attributes} (EdgeId is managed by the graph object itself)
		self.adjlist = {} # list of dictionaries: [Edge_1, Edge_2, ...] with Edge_i={Destination:EdgeId}
		self.radjlist = {} # Stores reverse edges in directed graphs. Used to remove nodes efficiently
		self.numedges = 0
		self.type = graphType # 'directed' or 'undirected'. TODO: add 'multiedge'

	def addNode(self, nodeId, attributes):
		self.nodes[nodeId] = attributes;

	def removeNode(self, nodeId):
		if nodeId in self.nodes:
			del self.nodes[nodeId]
		if nodeId in self.adjlist:
			for destId,edgeId in self.adjlist[nodeId].iteritems():
				del self.edges[edgeId]
				if self.type == 'undirected':
					del self.adjlist[destId][nodeId]
				elif self.type == 'directed':
					del self.radjlist[destId][nodeId]
			del self.adjlist[nodeId]

	def getNewEdgeId(self):
		newEdgeId = self.numedges
		self.numedges += 1
		return newEdgeId

	def addEdge(self, origin, destination, attr):
		# origin: ID of origin node
		# destination: ID of destination node
		# attr: attributes of edge
		if not origin in self.adjlist:
			self.adjlist[origin] = {}
		adjlist = self.adjlist[origin]
		if not destination in adjlist:
			edgeId = self.getNewEdgeId()
			adjlist[destination] = edgeId
		else:
			edgeId = adjlist[destination]
		if not edgeId in self.edges:
			self.edges[edgeId] = {}
		self.edges[edgeId].update(attr)
		if self.type == 'undirected':
			if not destination in self.adjlist:
				self.adjlist[destination] = {}
			self.adjlist[destination][origin] = edgeId
		elif self.type == 'directed':
			if not destination in self.radjlist:
				self.radjlist[destination] = {}
			self.radjlist[destination][origin] = edgeId

	def removeEdge(self, origin, destination):
		if origin in self.adjlist:
			if destination in self.adjlist[origin]:
				adjlist = self.adjlist[origin]
				edgeId = adjlist[destination]
				del self.edges[edgeId]
				adjlist.remove(destination)
				if self.type == 'undirected':
					del self.adjlist[destination][origin]
				elif self.type == 'directed':
					del self.radjlist[destination][origin]