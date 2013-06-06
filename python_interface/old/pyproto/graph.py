import string
import pdb

class Graph:

	# self.nodes: dictionary of nodes {NodeId:Attributes}
	# self.edges: stores edges with adjacency list:
	#			{NodeId:{OutEdges}}, OutEdges={DestNodeId:EdgeAttributes}

	def __init__(self, graphType, selfloop=True):
		self.nodes = {} # dictionary {NodeId:Attributes}
		self.edges = {} # dictionary {EdgeId:Attributes} (EdgeId is managed by the graph object itself)
		self.adjlist = {} # list of dictionaries: [Edge_1, Edge_2, ...] with Edge_i={Destination:EdgeId}
		self.radjlist = {} # Stores reverse edges in directed graphs. Used to remove nodes efficiently
		self.numedges = 0
		self.selfloop = selfloop
		self.type = graphType # 'directed' or 'undirected'. TODO: add 'multiedge'
		self.dumpcnt = 0

	def addNode(self, nodeId, attributes):
		if not nodeId in self.nodes:
			self.nodes[nodeId] = {}
			self.adjlist[nodeId] = {}
			if not self.type== 'undirected':
				self.radjlist[nodeId] = {}
		self.nodes[nodeId].update(attributes)

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

	def addEdge(self, source, destination, attr=[]):
		# source: ID of source node
		# destination: ID of destination node
		# attr: attributes of edge

		# Create nodes if necessary
		if not source in self.nodes:
			self.nodes[source] = {}
		if not destination in self.nodes:
			self.nodes[destination] = {}
		if not source in self.adjlist:
			self.adjlist[source] = {}
		adjlist = self.adjlist[source]

		# Check if edge is self-loop
		if (source == destination) and not self.selfloop:
			return

		# Create or find edge
		if self.type == 'multiedge':
			if not destination in adjlist:
				adjlist[destination] = []
			edgeId = self.getNewEdgeId()
			adjlist[destination].append(edgeId)
		else:
			if not destination in adjlist:
				edgeId = self.getNewEdgeId()
				adjlist[destination] = edgeId
			else:
				edgeId = adjlist[destination]

		# Write edge attributes
		if not edgeId in self.edges:
			self.edges[edgeId] = {}
		self.edges[edgeId].update(attr)

		# Write reverse edge
		if self.type == 'undirected':
			if not destination in self.adjlist:
				self.adjlist[destination] = {}
			self.adjlist[destination][source] = edgeId
		else:
			if not destination in self.radjlist:
				self.radjlist[destination] = {}
			radjlist = self.radjlist[destination]
			if self.type == 'multiedge':
				if not source in radjlist:
					radjlist[source] = []
				radjlist[source].append(edgeId)
			elif self.type == 'directed':
				radjlist[source] = edgeId

	def removeEdge(self, source, destination):
		if self.type == 'multiedge':
			raise NotImplementedError
			# In the multiedge case, remove all edges between source and destination
		if source in self.adjlist:
			if destination in self.adjlist[source]:
				adjlist = self.adjlist[source]
				edgeId = adjlist[destination]
				del self.edges[edgeId]
				adjlist.remove(destination)
				if self.type == 'undirected':
					del self.adjlist[destination][source]
				elif self.type == 'directed':
					del self.radjlist[destination][source]

	def removeEdgeById(self, edgeId):
		raise NotImplementedError

	def addNodes(self, table, nodeIdx, attributes=[]):
		pos = table.getPos(nodeIdx)
		for row in table.data:
			attrDict = table.getAttrDict(row,attributes)
			self.addNode(row[pos],attrDict)

	def addEdges(self, table, srcIdx, destIdx, attributes=[]):
		srcPos = table.getPos(srcIdx)
		destPos = table.getPos(destIdx)
		for row in table.data:
			attrDict = table.getAttrDict(row,attributes)
			self.addEdge(row[srcPos],row[destPos],attrDict)

	def numNodes(self):
		return len(self.nodes)

	def dump(self, n=-1, reset=False):
		if n==-1:
			n = self.self.numNodes()
		if reset:
			self.dumpcnt = 0
		nodewidth = 7
		nodes = self.nodes.keys()
		for i in [x+self.dumpcnt for x in range(n)]:
			if i >= len(nodes):
				break
			output = string.ljust(unicode(nodes[i])[:nodewidth],nodewidth) + "--> "
			output += ', '.join([unicode(destKey) for destKey in self.adjlist[nodes[i]].keys()])
			self.dumpcnt += 1
			print output