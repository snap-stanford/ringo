import sql
import graph
import condition
import pdb

WEIGHT_ATTR_NAME = "Weight"

class NodeDescription:
    def __init__(self,idAttr,filterCond=[],dataAttr=[]):
        self.idAttr = idAttr
        if not isinstance(filterCond,list):
            filterCond = [filterCond]
        self.filter = filterCond
        if not isinstance(dataAttr,list):
            dataAttr = [dataAttr]
        self.dataAttr = dataAttr

    def rename(self,oldAttr,newAttr):
        if self.idAttr == oldAttr:
            self.idAttr = newAttr
        # Should also rename other attributes (in dataAttr and filter).
        # But attributes names will be managed differently in the future

    def copy(self):
        return NodeDescription(self.idAttr,self.filter[:],self.dataAttr[:])

class EdgeDescription:
    def __init__(self,relation,edgeType="directed",threshold=None,dataAttr=[]):
        if not isinstance(relation,list):
            relation = [relation]
        self.relation = relation # A relation is a list of tuples of attributes (used for joining)
        self.type = edgeType
        self.threshold = threshold # Way more general edge filtering should be possible
        if not isinstance(dataAttr,list):
            dataAttr = [dataAttr]
        self.dataAttr = dataAttr

def link1(table,nodeDesc1,nodeDesc2,edgeDesc):
    # Create new graph and add nodes
    g = graph.Graph(edgeDesc.type,False)
    g.addNodes(table,nodeDesc1.idAttr)
    g.addNodes(table,nodeDesc2.idAttr)

    # Transform table to get edges
    nodeDesc2 = nodeDesc2.copy()
    # Are there meaningful examples with only one table, where the edge data is
    # already in the initial table? Most likely it is generated (for example, 
    # a weight can be generated during the grouping operation)
    relationAttr1 = [attr for attr,_ in edgeDesc.relation]
    relationAttr2 = [attr for _,attr in edgeDesc.relation]
    assert not (nodeDesc1.idAttr in relationAttr1 or nodeDesc2.idAttr in relationAttr2)
    projlist1 = [nodeDesc1.idAttr] + relationAttr1 + nodeDesc1.dataAttr
    projlist2 = [nodeDesc2.idAttr] + relationAttr2 + nodeDesc2.dataAttr
    t1 = sql.select(table, nodeDesc1.filter, projlist1)
    t2 = sql.select(table, nodeDesc2.filter, projlist2)

    # Make sure the nodeDesc attribute names won't be changed when joining
    # TODO: don't autorename in join, raise exceptions instead
    # TODO: The code below both too complicated and unsafe: in final implementation, maintain an attribute store, common to all tables
    if nodeDesc1.idAttr == nodeDesc2.idAttr:
        attr = nodeDesc1.idAttr
        newAttr1 = attr+'1'
        t1.rename(attr,newAttr1)
        nodeDesc1.rename(attr,newAttr1)
        #edgeDesc.rename(attr,newAttr1)
        newAttr2 = attr+'2'
        t2.rename(attr,newAttr2)
        nodeDesc2.rename(attr,newAttr2)
        #edgeDesc.rename(attr,newAttr2)
    for index,attr in enumerate(t1.columns):
        if attr == nodeDesc2.idAttr:
            newAttr = attr+'_'
            t1.rename(attr,newAttr) #(unsafe because the renamed attribute could be used somewhere else (e.g. in node data or relation)
    for index,attr in enumerate(t2.columns):
        if attr == nodeDesc1.idAttr:
            newAttr = attr+'_'
            t2.rename(attr,newAttr)
    t3 = sql.join(t1,t2,edgeDesc.relation)

    if edgeDesc.threshold:
        # We will probably want a more general kind of weight
        t4 = sql.group(t3,[nodeDesc1.idAttr,nodeDesc2.idAttr],WEIGHT_ATTR_NAME,"cnt")
    else:
        t4 = sql.group(t3,[nodeDesc1.idAttr,nodeDesc2.idAttr])

    t5 = sql.select(t4,condition.Condition(WEIGHT_ATTR_NAME,">=",edgeDesc.threshold))

    # Add edges to graph
    if edgeDesc.threshold:
        g.addEdges(t4,nodeDesc1.idAttr,nodeDesc2.idAttr,[WEIGHT_ATTR_NAME])
    else:
        g.addEdges(t4,nodeDesc1.idAttr,nodeDesc2.idAttr)
    return g

# Node description:
#   id (attribute name)
#   filter (condition on some attributes)
#   attributes (attributes in the table, other than ID)