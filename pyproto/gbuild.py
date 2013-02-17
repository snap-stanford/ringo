import table
import graph
from sql import select, project, rename, join, group, order, expand
from condition import Condition

#	---------------------------------------------
#		Graph 1 : Question and Answer Graph
#	---------------------------------------------

# Query: "select P1.OwnerUserId as UserId1, 
# P2.OwnerUserId as UserId2, count(UserId1) as Count from posts P1, posts P2 where P1.PostTypeId = 1 
# and P2.PostTypeId = 2 group by UserId1, UserId2"
def CG1():
	t1 = table.Table("data/posts.xml")
	t2 = select(t1, "PostTypeId", Condition("==", 1)) #Questions
	t3 = select(t1, "PostTypeId", Condition("==", 2)) #Answers
	t4 = join(t3,t2,["ParentId"],["Id"],["OwnerUserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
	t5 = group(t4, ["UserId1", "UserId2"], "Count", "cnt")
	g = graph.Graph("directed")
	g.addNodes(t1,"OwnerUserId")
	g.addEdges(t5,"UserId1","UserId2",["Count"])
	return g

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
	g = graph.Graph("directed")
	g.addNodes(t1,"OwnerUserId")
	g.addNodes(t2,"UserId")
	g.addEdges(t5,"UserId1","UserId2",["Count"])
	return g

#	---------------------------------------------
#		Graph 3 : Comments Graph
#	---------------------------------------------

# Query: "select P.OwnerUserId as UserId1, C.UserId as UserId2 from posts P, 
# comments C group by UserId1, UserId2"
def CG3():
	t1 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...]   
	t2 = table.Table("data/comments.xml") #["PostId","UserId","Text",...]
	t3 = join(t2,t1,["PostId"],["Id"],["UserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
	g = graph.Graph("multiedge")
	g.addNodes(t1,"OwnerUserId")
	g.addNodes(t2,"UserId")
	g.addEdges(t3,"UserId1","UserId2")
	return g

#	--------------------------------------------------------------
#		Graph 4 : Common Comments (similar to Common Votes)
#	--------------------------------------------------------------

def CG4(thresh):
	t1 = table.Table("data/comments.xml")
	t2 = join(t1,t1,["PostId"],["PostId"],["UserId"],["UserId"],["PostId","UserId1","UserId2"])
	t3 = group(t2,["UserId1","UserId2"],"Count","cnt")
	t4 = select(t3,"Count",Condition(">=",thresh))
	g = graph.Graph("undirected",False)
	g.addNodes(t1,"UserId")
	g.addEdges(t4,"UserId1","UserId2",["Count"])
	return g

#	--------------------------------------------------------------
#		Graph 5 : Common Commenters (similar to Common Voters)
#	--------------------------------------------------------------

def CG5(thresh):
	t1 = table.Table("data/comments.xml")
	t2 = join(t1,t1,["UserId"],["UserId"],["PostId"],["PostId"],["UserId","PostId1","PostId2"])
	t3 = group(t2,["PostId1","PostId2"],"Count","cnt")
	t4 = select(t3,"Count",Condition(">=",thresh))
	g = graph.Graph("undirected",False)
	g.addNodes(t1,"PostId")
	g.addEdges(t4,"PostId1","PostId2",["Count"])
	return g

#	--------------------------------------------------------------
#		Graph 7 : Same Editors
#	--------------------------------------------------------------

def CG7():
	t1 = table.Table("data/posthistory.xml")
	t2 = group(t1,["PostId","UserId"])
	t3 = join(t2,t2,["UserId"],["UserId"],["PostId"],["PostId"],["UserId","PostId1","PostId2"])
	t4 = group(t3,["PostId1","PostId2"])
	g = graph.Graph("undirected",False)
	g.addNodes(t1,"PostId")
	g.addEdges(t4,"PostId1","PostId2")
	return g

#	--------------------------------------------------------------
#		Graph 8 : Dates
#	--------------------------------------------------------------

def CG8():
	t1 = table.Table("data/posthistory.xml")
	t2 = group(t1,["UserId"],["PostId","CreationDate"],"list")
	t3 = order(t2,"PostId","CreationDate") # In each row, order postIds by date
	t4 = expand(t3) # Generate table with one row for each consecutive pair of postIds in each row of the original table
	g = graph.Graph("directed",False)
	g.addNodes(t1,"PostId")
	g.addEdges(t4,"PostId1","PostId2")
	return g

#	---------------------------------------------
#		Graph 9 : Badges Graph
#	---------------------------------------------
# Query: "select P.OwnerUserId as UserId1, 
# V.UserId as UserId2, count(UserId1) as Count from posts P, votes V where V.VoteTypeId = 2 
# group by UserId1, UserId2" 
def CG9():
	t1 = table.Table("data/badges.xml") #[UserId","Name"...]
	t2 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...]
	t3 = join(t1,t2,["UserId"],["OwnerUserId"],["Name"],["PostTypeId","ParentId","Id"])
	t4 = select(t3, "PostTypeId", Condition("==", 1)) #Questions
	t5 = select(t3, "PostTypeId", Condition("==", 2)) #Answers
	t6 = join(t5,t4,["ParentId"],["Id"],["Name"],["Name"],["Id","Badge1","Badge2"])
	t7 = group(t6,["Badge1","Badge2"],"Count","cnt")
	g = graph.Graph("directed")
	g.addNodes(t1,"Name")
	g.addEdges(t7,"Badge1","Badge2",["Count"])
	return g
