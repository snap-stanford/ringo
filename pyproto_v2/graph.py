import string

class Graph:

	def __init__(self, gtype):
		self.nodes = {} # dictionary {NodeId:Attributes}
		self.edges = {} # dictionary {EdgeId:Attributes} (EdgeId is managed by the graph object itself)
		self.nodeIdDict = {} # dictionary {NodeTuple:NodeId}
		self.rNodeIdDict = {} # reverse dictionary
		self.adjlist = {} # dictionary {NodeId:EdgeDict} with EdgeDict={DestId:[EdgeIds]}
		self.radjlist = {} # Stores reverse edges in directed graphs. Used to remove nodes efficiently
		self.numedges = 0
		self.numnodes = 0
		self.type = gtype # 'directed' or 'undirected'.
		self.dumpcnt = 0

	def addnode(self, node, attributes):
		if not node in self.nodeIdDict:
			nodeId = self.getNewNodeId()
			self.nodeIdDict[node] = nodeId
			self.rNodeIdDict[nodeId] = node
			self.nodes[nodeId] = {}
			self.adjlist[nodeId] = {}
			if not self.type == 'undirected':
				self.radjlist[nodeId] = {}
		else:
			nodeId = self.nodeIdDict[node]
		self.nodes[nodeId].update(attributes)

	def addedge(self, src, dest, attr=[]):
		# Create edge (edges cannot be updated, if addedge is called twice
		# with the same source and destination, then the graph is multiedge)
		srcId = self.nodeIdDict[src]
		destId = self.nodeIdDict[dest]
		edgeId = self.getNewEdgeId()
		if not destId in self.adjlist[srcId]:
			self.adjlist[srcId][destId] = []
		self.adjlist[srcId][destId].append(edgeId)
		self.edges[edgeId] = attr
		# Write reverse edge
		if self.type == 'undirected':
			if not srcId in self.adjlist[destId]:
				self.adjlist[destId][srcId] = []
			self.adjlist[destId][srcId].append(edgeId)
		elif self.type == 'directed':
			if not srcId in self.radjlist[destId]:
				self.radjlist[destId][srcId] = []
			self.radjlist[destId][srcId].append(edgeId)

	def removenode(self, node):
		if node in self.nodeIdDict:
			nodeId = self.nodeIdDict[node]
			del self.nodes[nodeId]
			del self.nodeIdDict[node]
			del self.rNodeIdDict[nodeId]
			for destId,edgeIds in self.adjlist[nodeId].iteritems():
				for edgeId in edgeIds:
					del self.edges[edgeId]
				if self.type == 'undirected':
					del self.adjlist[destId][nodeId]
				elif self.type == 'directed':
					del self.radjlist[destId][nodeId]
			del self.adjlist[nodeId]
			if self.type == 'directed':
				del self.radjlist[nodeId]

	def removeedges(self, src, dest):
		# Removes all edges between a given source and destination
		if src in self.nodeIdDict and dest in self.nodeIdDict:
			srcId = self.nodeIdDict[src]
			destId = self.nodeIdDict[dest]
			if srcId in self.adjlist:
				if destId in self.adjlist[srcId]:
					edgeIds = self.adjlist[srcId][destId]
					for edgeId in edgeIds:
						del self.edges[edgeId]
					del self.adjlist[srcId][destId]
					if self.type == 'undirected':
						del self.adjlist[destId][srcId]
					elif self.type == 'directed':
						del self.radjlist[destId][srcId]

	def dump(self, n=-1, reset=False):
		if n==-1:
			n = self.numnodes
		if reset:
			self.dumpcnt = 0
		nodewidth = 7
		nodes = self.nodeIdDict.keys()
		for i in [x+self.dumpcnt for x in range(n)]:
			if i >= len(nodes):
				break
			node = nodes[i]
			nodeId = self.nodeIdDict[node]
			output = string.ljust(unicode(node)[:nodewidth],nodewidth) + "--> "
			output += ', '.join([unicode(self.rNodeIdDict[destId]) for destId in self.adjlist[nodeId].keys()])
			self.dumpcnt += 1
			print output

	def getNewNodeId(self):
		newNodeId = self.numnodes
		self.numnodes += 1
		return newNodeId
	def getNewEdgeId(self):
		newEdgeId = self.numedges
		self.numedges += 1
		return newEdgeId