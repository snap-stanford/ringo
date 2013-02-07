import table
import gsql

def makeGraph(table, attr1, attr2, graphType):
	nodes = {}
	for row in table:
		node1 = table.getElem(row, attr1)
		node2 = table.getElem(row, attr2)
		edges = nodes[node1]
		edge = Edge(node2, [])
		if edge not in edges:
			edges[node2] = edge
		nodes[node1] = edges

	graph = Graph(table, nodes, graphType)
	return graph

t1 = Table("posts.xml")
t2 = select(t1, "PostTypeId", "=", 1)
t3 = select(t1, "PostTypeId", "=", 2)
t4 = project(t2, ["Id", "OwnerUserId"])
t5 = project(t3, ["ParentId", "OwnerUserId"])
t6 = rename(t5, "ParentId", "Id")
t7 = rename(t4, "OwnerUserId", "UserId1")
t8 = rename(t6, "OwnerUserId", "UserId2")
t9 = join(t7, t8)
t10 = group(t9, ["UserId1", "UserId2"], "count", "Count")

makeGraph(t10, "UserId1", "UserId2", "directed")




