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

#	---------------------------------------------
#		Graph 1 : Question and Answer Graph
#	---------------------------------------------

# Query: “select P1.OwnerUserId as UserId1, 
# P2.OwnerUserId as UserId2, count(UserId1) as Count from posts P1, posts P2 where P1.PostTypeId = 1 
# and P2.PostTypeId = 2 group by UserId1, UserId2” 
t1 = Table("posts.xml")
t2 = select(t1, "PostTypeId", Condition("=", 1))
t3 = select(t1, "PostTypeId", "=", 2)
t4 = project(t2, ["Id", "OwnerUserId"])
t5 = project(t3, ["ParentId", "OwnerUserId"])
t6 = rename(t5, "ParentId", "Id")
t7 = rename(t4, "OwnerUserId", "UserId1")
t8 = rename(t6, "OwnerUserId", "UserId2")
t9 = join(t7, t8)
t10 = group(t9, ["UserId1", "UserId2"], "count", "Count")

makeGraph(t10, "UserId1", "UserId2", "directed")

#	---------------------------------------------
#		Graph 2 : Voting Graph
#	---------------------------------------------

# Query: “select P.OwnerUserId as UserId1, 
# V.UserId as UserId2, count(UserId1) as Count from posts P, votes V where V.VoteTypeId = 2 
# group by UserId1, UserId2” 
t1 = Table("posts.xml") #[“Id”,”PostTypeId”,”OwnerUserId”,...] 
t2 = Table("votes.xml") #[“PostId”,”VoteTypeId”,”UserId”,...]  
t3 = select(t2,"VoteTypeId", Condition("=", 2))
t4 = project(t1,["Id","OwnerUserId"])
t5 = project(t3,["PostId", "UserId"])
t6 = rename(t5,"UserId", "UserId1")
t7 = rename(t4,"OwnerUserId", "UserId2")
t8 = rename(t6,"PostId","Id")
t9 = join(t7,t8)
t10 = group(t9,[“UserId1”,”UserId2”],”count”,”Count”)
makegraph(t10,”UserId1”,”UserId2”, "directed")

#	---------------------------------------------
#		Graph 3 : Comments Graph
#	---------------------------------------------

# Query: "select P.OwnerUserId as UserId1, C.UserId as UserId2 from posts P, 
# comments C group by UserId1, UserId2"
t1 = Table("posts.xml") #[“Id”,”PostTypeId”,”OwnerUserId”,...]   
t2 = Table("comments.xml") #[“PostId”,”UserId”,”Text”,...]
t3 = project(t1,[“Id”,”OwnerUserId”])
t4 = project(t2,[“PostId”,”UserId”,”Text”])
t5 = rename(t4,”UserId", "UserId1”)
t6= rename(t3,”OwnerUserId", "UserId2”)
t7 = rename(t5,“PostId", "Id”)
t8 = join(t6,t7)
makegraph(t8,”UserId1”,”UserId2”,"directed")

