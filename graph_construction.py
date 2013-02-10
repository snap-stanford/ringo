import table
import graph
from sql import select, project, rename, join, group
from condition import Condition

def makeGraph(table, srcAttr, destAttr, graphType):
	g = graph.Graph(graphType)
	source = table.getColumnByAttr(srcAttr)
	destination = table.getColumnByAttr(destAttr)
	for src,dest in zip(source,destination):
		g.addEdge(src,dest,{})
	return g

#	---------------------------------------------
#		Graph 1 : Question and Answer Graph
#	---------------------------------------------

# Query: "select P1.OwnerUserId as UserId1, 
# P2.OwnerUserId as UserId2, count(UserId1) as Count from posts P1, posts P2 where P1.PostTypeId = 1 
# and P2.PostTypeId = 2 group by UserId1, UserId2"
def CG1():
	t1 = table.Table("data/posts.xml")
	t2 = select(t1, "PostTypeId", Condition("==", 1))
	t3 = select(t1, "PostTypeId", Condition("==", 2))
	t4 = join(t2,t3,["Id"],["ParentId"],["OwnerUserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
	t5 = group(t4, ["UserId1", "UserId2"], "Count", "cnt")
	return makeGraph(t5, "UserId1", "UserId2", "directed")

#	---------------------------------------------
#		Graph 2 : Voting Graph
#	---------------------------------------------
# Query: "select P.OwnerUserId as UserId1, 
# V.UserId as UserId2, count(UserId1) as Count from posts P, votes V where V.VoteTypeId = 2 
# group by UserId1, UserId2" 
def CG2():
	t1 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...] 
	t2 = table.Table("data/votes.xml") #["PostId","VoteTypeId","UserId",...]  
	t3 = select(t2,"VoteTypeId", Condition("==", 2))
	t4 = join(t3,t1,["PostId"],["Id"],["UserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
	t5 = group(t4,["UserId1","UserId2"], "Count","cnt")
	return makeGraph(t5,"UserId1","UserId2","directed")

#	---------------------------------------------
#		Graph 3 : Comments Graph
#	---------------------------------------------

# Query: "select P.OwnerUserId as UserId1, C.UserId as UserId2 from posts P, 
# comments C group by UserId1, UserId2"
def CG3():
	t1 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...]   
	t2 = table.Table("data/comments.xml") #["PostId","UserId","Text",...]
	t3 = join(t2,t1,["PostId"],["Id"],["UserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
	return makeGraph(t3,"UserId1","UserId2","multiedge")
