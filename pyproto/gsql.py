import sql
import graph
import condition
import pdb
import util

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
    # Get attributes indexes
    node1Idx = table.getIndex(nodeDesc1.idAttr)
    node2Idx = table.getIndex(nodeDesc2.idAttr)
    relationAttr1 = [attr for attr,_ in edgeDesc.relation]
    relationAttr2 = [attr for _,attr in edgeDesc.relation]
    node1RelIdx = table.getIndex(relationAttr1)
    node2RelIdx = table.getIndex(relationAttr2)
    node1DataIdx = table.getIndex(nodeDesc1.dataAttr)
    node2DataIdx = table.getIndex(nodeDesc2.dataAttr)
    # Create new graph and add nodes
    g = graph.Graph(edgeDesc.type,False)
    g.addNodes(table,node1Idx)
    g.addNodes(table,node2Idx)
    # Tranform table
    assert not (node1Idx in node1RelIdx or node2Idx in node2RelIdx)
    projlist1 = [node1Idx] + node1RelIdx + node1DataIdx
    projlist2 = [node2Idx] + node2RelIdx + node2DataIdx
    for cond in nodeDesc1.filter+nodeDesc2.filter:
        cond.configureForTable(table)
    t1,idxmap1 = table.select(nodeDesc1.filter, projlist1)
    t2,idxmap2 = table.select(nodeDesc2.filter, projlist2)
    t3,idxmap3 = t1.join(t2,zip(util.mapIdx(node1RelIdx,idxmap1),util.mapIdx(node2RelIdx,idxmap2)))
    if edgeDesc.threshold:
        t4,idxmap4 = t3.group([util.mapIdx(node1Idx,idxmap1,idxmap3),util.mapIdx(node2Idx,idxmap2,idxmap3)],True)
        t5,idxmap5 = t4.select(condition.Condition(WEIGHT_ATTR_NAME,">=",edgeDesc.threshold))
        idxmap = util.mergeIdxmap(idxmap4,idxmap5)
    else:
        t5,idxmap = t3.group([util.mapIdx(node1Idx,idxmap1,idxmap3),util.mapIdx(node2Idx,idxmap2,idxmap3)],False)
    # Add edges
    g.addEdges(t5,util.mapIdx(node1Idx,idxmap1,idxmap3,idxmap),util.mapIdx(node2Idx,idxmap2,idxmap3,idxmap))
    pdb.set_trace()
    return g

# Node description:
#   id (attribute name)
#   filter (condition on some attributes)
#   attributes (attributes in the table, other than ID)