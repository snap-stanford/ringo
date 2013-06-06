# CG1
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/posts.xml")
t2 = select(t1, Condition("PostTypeId","==", 1), ["Id","OwnerUserId"])
t3 = select(t1, Condition("PostTypeId","==", 2), ["ParentId","OwnerUserId"])
t4 = join(t2,t3,[("Id","ParentId")])
t5 = group(t4, ["OwnerUserId1", "OwnerUserId2"], "Count", "cnt")
g = graph.Graph("directed")
g.addNodes(t1,"OwnerUserId",[])
g.addEdges(t5,"UserId1","UserId2",["Count"])

# CG2
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...] 
t2 = table.Table("data/votes.xml") #["PostId","VoteTypeId","UserId",...]  
t3 = select(t2, Condition("VoteTypeId", "==", 2))
t4 = join(t3,t1,["PostId"],["Id"],["UserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
t5 = group(t4,["UserId1","UserId2"], "Count","cnt")
g = graph.Graph("directed")
g.addNodes(t1,"OwnerUserId",[])
g.addNodes(t2,"UserId",[])
g.addEdges(t5,"UserId1","UserId2",["Count"])

# CG3
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...]   
t2 = table.Table("data/comments.xml") #["PostId","UserId","Text",...]
t3 = join(t2,t1,["PostId"],["Id"],["UserId"],["OwnerUserId"],["Id","UserId1","UserId2"])
g = makeGraph(t3,"UserId1","UserId2","multiedge")

# CG4
thresh = 10
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/comments.xml")
t2 = join(t1,t1,["PostId"],["PostId"],["UserId"],["UserId"],["PostId","UserId1","UserId2"])
t3 = group(t2,["UserId1","UserId2"],"Count","cnt")
t4 = select(t3,Condition("Count",">=",thresh))
g = makeGraph(t4,"UserId1","UserId2","undirected",False)

# CG5
thresh = 10
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/comments.xml")
t2 = join(t1,t1,["UserId"],["UserId"],["PostId"],["PostId"],["UserId","PostId1","PostId2"])
t3 = group(t2,["PostId1","PostId2"],"Count","cnt")
t4 = select(t3,Condition("Count",">=",thresh))
g = makeGraph(t4,"PostId1","PostId2","undirected",False)

# CG7
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/posthistory.xml")
t2 = group(t1,["PostId","UserId"])
t3 = join(t2,t2,["UserId"],["UserId"],["PostId"],["PostId"],["UserId","PostId1","PostId2"])
t4 = group(t3,["PostId1","PostId2"])
g = makeGraph(t4,"PostId1","PostId2","undirected",False)

#CG8
import table
import graph
import sql
from condition import Condition
t1 = table.Table("data/posthistory.xml")
t2 = sql.group(t1,["UserId"],["PostId","CreationDate"],"list")
t3 = sql.order(t2,"PostId","CreationDate") # In each row, order postIds by date
t4 = sql.expand(t3) # Generate table with one row for each consecutive pair of postIds in each row of the original table
g = graph.Graph("directed",False)
g.addNodes(t1,"PostId")
g.addEdges(t4,"PostId1","PostId2")

# CG9
import table
import graph
from gbuild import makeGraph
from sql import select, project, rename, join, group
from condition import Condition
t1 = table.Table("data/badges.xml") #[UserId","Name"...]
t2 = table.Table("data/posts.xml") #["Id","PostTypeId","OwnerUserId",...]
t3 = join(t1,t2,["UserId"],["OwnerUserId"],["Name"],["PostTypeId","ParentId","Id"])
t4 = select(t3, Condition("PostTypeId", "==", 1)) #Questions
t5 = select(t3, Condition("PostTypeId", "==", 2)) #Answers
t6 = join(t5,t4,["ParentId"],["Id"],["Name"],["Name"],["Id","Badge1","Badge2"])
t7 = group(t6,["Badge1","Badge2"],"Count","cnt")
g = graph.Graph("directed")
g.addNodes(t1,"Name")
g.addEdges(t7,"Badge1","Badge2",["Count"])
