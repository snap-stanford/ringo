# coding: utf-8
import hashlib
import math
import os
import re
import unittest
import sys
sys.path.append("../ringo-engine-python")
import ringo

ringo = ringo.Ringo()

PATH_TO_GNUTELLA = "data/p2p-Gnutella08.txt"

class SnapPythonTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.gnutella = ringo.LoadEdgeList(ringo.PNGraph, PATH_TO_GNUTELLA, 0, 1)
        super(SnapPythonTest, self).__init__(*args, **kwargs)

    def setUp(self):
        # Defaults for creating graphs
        self.num_nodes = 10

        # Full Graphs
        self.DirGraphFull = ringo.GenFull(ringo.PNGraph, self.num_nodes)
        self.UnDirGraphFull = ringo.GenFull(ringo.PUNGraph, self.num_nodes)
        self.NetFull = ringo.GenFull(ringo.PNEANet, self.num_nodes)

        # Star Graphs
        self.DirGraphStar = ringo.GenStar(ringo.PNGraph, self.num_nodes)
        self.UnDirGraphStar = ringo.GenStar(ringo.PUNGraph, self.num_nodes)
        self.NetStar = ringo.GenStar(ringo.PNEANet, self.num_nodes)

        # Graph With Self Edges
        self.DirGraphSelfEdge = ringo.GenRndGnm(ringo.PNGraph, 10, 20)
        self.DirGraphSelfEdge.AddEdge(0, 0)
        self.UnDirGraphSelfEdge = ringo.GenRndGnm(ringo.PUNGraph, 10, 20)
        self.UnDirGraphSelfEdge.AddEdge(0, 0)
        self.NetSelfEdge = ringo.GenRndGnm(ringo.PNEANet, 10, 20)
        self.NetSelfEdge.AddEdge(0, 0)

        # Graph With Multiple Zero-Degree Nodes
        self.DirGraphZeroDegree = ringo.GenRndGnm(ringo.PNGraph, 10, 1)
        self.UnDirGraphZeroDegree = ringo.GenRndGnm(ringo.PUNGraph, 10, 1)
        self.NetZeroDegree = ringo.GenRndGnm(ringo.PNEANet, 10, 1)

        # Trees
        self.DirTree = ringo.GenTree(ringo.PNGraph, 3, 3)
        self.UnDirTree = ringo.GenTree(ringo.PUNGraph, 3, 3)
        self.NetTree = ringo.GenTree(ringo.PNEANet, 3, 3)

        # Random
        self.DirRand = ringo.GenRndGnm(ringo.PNGraph, 10, 20)
        self.UnDirRand = ringo.GenRndGnm(ringo.PUNGraph, 10, 20)
        self.NetRand = ringo.GenRndGnm(ringo.PNEANet, 10, 20)



    #### Helper Functions for Tests ####

    def checkPlotHash(self, gen_file, exp_hash):
        test_file = 'test.txt'
        self.assertTrue(os.path.isfile(gen_file))
        os.system('grep -v "^#" ' + gen_file + '  > ' + test_file)
        act_hash = hashlib.md5(open(test_file, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, act_hash)
        os.system('rm ' + test_file)

    def checkPrintInfoOutput(self, filename, params):
        count = 0
        with open(filename) as f:
            for line in f:
                if count == 0:
                    firstLine = line.split(':')
                    self.assertEqual(params[count], firstLine[0])
                else:
                    result = re.findall('[0-9]+', line)
                    self.assertEqual(params[count], result[0])
                count += 1



    #### Tests ####
    def test_CntInDegNodes(self):
        # Directed graph
        num_nodes = ringo.CntInDegNodes(self.DirGraphFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

        # Undirected Graph
        num_nodes = ringo.CntInDegNodes(self.UnDirGraphFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

        # Network
        num_nodes = ringo.CntInDegNodes(self.NetFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

    def test_CntOutDegNodes(self):
        # Directed Graph
        num_nodes = ringo.CntOutDegNodes(self.DirGraphFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

        # Undirected Graph
        num_nodes = ringo.CntOutDegNodes(self.UnDirGraphFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

        # Network
        num_nodes = ringo.CntOutDegNodes(self.NetFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

    def test_CntDegNodes(self):
        # Directed Graph - it will have twice the edges as the undirected graph
        num_nodes = ringo.CntDegNodes(self.DirGraphFull, 2*(self.num_nodes-1))
        self.assertEqual(self.num_nodes, num_nodes)

        # Undirected Graph
        num_nodes = ringo.CntDegNodes(self.UnDirGraphFull, self.num_nodes-1)
        self.assertEqual(self.num_nodes, num_nodes)

        # Network
        num_nodes = ringo.CntDegNodes(self.NetFull, 2*(self.num_nodes-1))
        self.assertEqual(self.num_nodes, num_nodes)

    def test_CntNonZNodes(self):
        # Directed Graph
        num_nodes = ringo.CntNonZNodes(self.DirGraphFull)
        self.assertEqual(self.num_nodes, num_nodes)

        # Undirected Graph
        num_nodes = ringo.CntNonZNodes(self.UnDirGraphFull)
        self.assertEqual(self.num_nodes, num_nodes)

        # Network
        num_nodes = ringo.CntNonZNodes(self.NetFull)
        self.assertEqual(self.num_nodes, num_nodes)

    def test_GetMxDegNId(self):
        # Directed Graph
        max_id = ringo.GetMxDegNId(self.DirGraphStar)
        self.assertEqual(0, max_id)

        # Undirected Graph
        max_id = ringo.GetMxDegNId(self.UnDirGraphStar)
        self.assertEqual(0, max_id)

        # Network
        max_id = ringo.GetMxDegNId(self.NetStar)
        self.assertEqual(0, max_id)

    def test_GetMxInDegNId(self):
        # Directed Graph
        max_id = ringo.GetMxInDegNId(self.DirGraphStar)
        # node with id 0 is the only node with in-degree 0
        self.assertNotEqual(0, max_id)

        # Undirected Graph
        max_id = ringo.GetMxInDegNId(self.UnDirGraphStar)
        self.assertEqual(0, max_id)

        # Network
        max_id = ringo.GetMxInDegNId(self.NetStar)
        # node with id 0 is the only node with in-degree 0
        self.assertNotEqual(0, max_id)

    def test_GetMxOutDegNId(self):
        # Directed Graph
        max_id = ringo.GetMxOutDegNId(self.DirGraphStar)
        self.assertEqual(0, max_id)

        # Undirected Graph
        max_id = ringo.GetMxOutDegNId(self.UnDirGraphStar)
        self.assertEqual(0, max_id)

        # Network
        max_id = ringo.GetMxOutDegNId(self.NetStar)
        self.assertEqual(0, max_id)

    def test_GetInDegCnt(self):
        # Directed Graph
        DegToCntV = ringo.GetInDegCnt(self.DirGraphFull)
        # There should be only one entry (num_nodes -1, num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

        # Undirected Graph
        DegToCntV = ringo.GetInDegCnt(self.UnDirGraphFull)
        # There should be only one entry (num_nodes -1, num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

        # Network
        DegToCntV = ringo.GetInDegCnt(self.NetFull)
        # There should be only one entry (num_nodes -1, num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

    def test_GetOutDegCnt(self):
        # Directed Graph
        DegToCntV = ringo.GetOutDegCnt(self.DirGraphFull)
        # There should be only one entry (num_nodes -1, num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

        # Undirected Graph
        DegToCntV = ringo.GetOutDegCnt(self.UnDirGraphFull)
        # There should be only one entry (num_nodes -1, num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

        # Network
        DegToCntV = ringo.GetOutDegCnt(self.NetFull)
        # There should be only one entry (2*(num_nodes-1), num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

    def test_GetDegCnt(self):
        # Directed Graph
        DegToCntV = ringo.GetDegCnt(self.DirGraphFull)
        # There should be only one entry (2*(num_nodes-1), num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(2*(self.num_nodes-1), item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

        # Undirected Graph
        DegToCntV = ringo.GetDegCnt(self.UnDirGraphFull)
        # There should be only one entry (num_nodes-1, num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal1())
            self.assertEqual(self.num_nodes, item.GetVal2())

        # Network
        DegToCntV = ringo.GetDegCnt(self.NetFull)
        # There should be only one entry (2*(num_nodes-1), num_nodes) in DegToCntV
        for item in DegToCntV:
            self.assertEqual(self.num_nodes, item.GetVal2())

    def test_GetNodeInDegV(self):
        # Directed Graph
        DegToCntV = ringo.GetNodeInDegV(self.DirGraphFull)
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal2())

        # Undirected Graph
        DegToCntV = ringo.GetNodeInDegV(self.UnDirGraphFull)
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal2())

        # Network
        DegToCntV = ringo.GetNodeInDegV(self.NetFull)
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal2())

    def test_GetNodeOutDegV(self):
        # Directed Graph
        DegToCntV = ringo.GetNodeOutDegV(self.DirGraphFull)
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal2())

        # Undirected Graph
        DegToCntV = ringo.GetNodeOutDegV(self.UnDirGraphFull)
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal2())

        # Network
        DegToCntV = ringo.GetNodeOutDegV(self.NetFull)
        for item in DegToCntV:
            self.assertEqual(self.num_nodes-1, item.GetVal2())

    def test_CntUniqUndirEdges(self):
        # Directed Graph
        num_edges = ringo.CntUniqUndirEdges(self.DirGraphFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1)/2, num_edges)

        # Unidrected Graph
        num_edges = ringo.CntUniqUndirEdges(self.UnDirGraphFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1)/2, num_edges)

        # Network
        num_edges = ringo.CntUniqUndirEdges(self.NetFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1)/2, num_edges)

    def test_CntUniqDirEdges(self):
        # Directed Graph
        num_edges = ringo.CntUniqDirEdges(self.DirGraphFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1), num_edges)

        # Unidrected Graph
        num_edges = ringo.CntUniqDirEdges(self.UnDirGraphFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1), num_edges)

        # Network
        num_edges = ringo.CntUniqDirEdges(self.NetFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1), num_edges)

    def test_CntUniqBiDirEdges(self):
        # Directed Graph
        num_edges = ringo.CntUniqBiDirEdges(self.DirGraphFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1)/2, num_edges)

        # Unidrected Graph
        num_edges = ringo.CntUniqBiDirEdges(self.UnDirGraphFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1)/2, num_edges)

        # Network
        num_edges = ringo.CntUniqBiDirEdges(self.NetFull)
        self.assertEqual(self.num_nodes * (self.num_nodes - 1)/2, num_edges)

    def test_CntSelfEdges(self):
        # Directed Graph
        num_edges = ringo.CntSelfEdges(self.DirGraphFull)
        self.assertEqual(0, num_edges)

        # Undirected Graph
        num_edges = ringo.CntSelfEdges(self.UnDirGraphFull)
        self.assertEqual(0, num_edges)

        # Network
        num_edges = ringo.CntSelfEdges(self.NetFull)
        self.assertEqual(0, num_edges)

    def test_GetUnDir(self):
        # Directed Graph
        New_Graph = ringo.GetUnDir(self.DirGraphStar)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(New_Graph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(New_Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(New_Graph.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))

        # Undirected Graph
        New_Graph = ringo.GetUnDir(self.UnDirGraphStar)
        for node in self.UnDirGraphStar.Nodes():
            self.assertTrue(New_Graph.IsNode(node.GetId()))
        for edge in self.UnDirGraphStar.Edges():
            self.assertTrue(New_Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(New_Graph.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))

        # Network
        New_Graph = ringo.GetUnDir(self.NetStar)
        for node in self.NetStar.Nodes():
            self.assertTrue(New_Graph.IsNode(node.GetId()))
        for edge in self.NetStar.Edges():
            self.assertTrue(New_Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(New_Graph.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))

    def test_MakeUnDir(self):
        # Directed Graph
        New_Graph = self.DirGraphStar
        ringo.MakeUnDir(New_Graph)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(New_Graph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(New_Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(New_Graph.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))

        # Undirected Graph
        New_Graph = self.UnDirGraphStar
        ringo.MakeUnDir(New_Graph)
        for node in self.UnDirGraphStar.Nodes():
            self.assertTrue(New_Graph.IsNode(node.GetId()))
        for edge in self.UnDirGraphStar.Edges():
            self.assertTrue(New_Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(New_Graph.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))

        # Network
        New_Graph = self.NetStar
        ringo.MakeUnDir(New_Graph)
        for node in self.NetStar.Nodes():
            self.assertTrue(New_Graph.IsNode(node.GetId()))
        for edge in self.NetStar.Edges():
            self.assertTrue(New_Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(New_Graph.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))

    def test_AddSelfEdges(self):
        # Directed Graph
        Graph_Copy = self.DirGraphFull
        ringo.AddSelfEdges(Graph_Copy)
        for node in Graph_Copy.Nodes():
            self.assertTrue(Graph_Copy.IsEdge(node.GetId(), node.GetId()))

        # Undirected Graph
        Graph_Copy = self.UnDirGraphFull
        ringo.AddSelfEdges(Graph_Copy)
        for node in Graph_Copy.Nodes():
            self.assertTrue(Graph_Copy.IsEdge(node.GetId(), node.GetId()))

        # Network
        Graph_Copy = self.NetFull
        ringo.AddSelfEdges(Graph_Copy)
        for node in Graph_Copy.Nodes():
            self.assertTrue(Graph_Copy.IsEdge(node.GetId(), node.GetId()))

    def test_DelSelfEdges(self):
        # Directed Graph
        Graph_Copy = self.DirGraphSelfEdge
        ringo.DelSelfEdges(Graph_Copy)
        for node in Graph_Copy.Nodes():
            self.assertFalse(Graph_Copy.IsEdge(node.GetId(), node.GetId()))

        # Undirected Graph
        Graph_Copy = self.UnDirGraphSelfEdge
        ringo.DelSelfEdges(Graph_Copy)
        for node in Graph_Copy.Nodes():
            self.assertFalse(Graph_Copy.IsEdge(node.GetId(), node.GetId()))

        # Network
        Graph_Copy = self.NetSelfEdge
        ringo.DelSelfEdges(Graph_Copy)
        for node in Graph_Copy.Nodes():
            self.assertFalse(Graph_Copy.IsEdge(node.GetId(), node.GetId()))

    def test_DelNodes(self):
        # Directed Graph
        Graph_Copy = self.DirGraphFull
        DelNodes = ringo.ConstructTIntV()
        DelNodes.Add(0)
        ringo.DelNodes(Graph_Copy, DelNodes)
        for node in DelNodes:
            self.assertFalse(Graph_Copy.IsNode(node))

        # Undirected Graph
        Graph_Copy = self.UnDirGraphFull
        DelNodes = ringo.ConstructTIntV()
        DelNodes.Add(0)
        ringo.DelNodes(Graph_Copy, DelNodes)
        for node in DelNodes:
            self.assertFalse(Graph_Copy.IsNode(node))

        # Network
        Graph_Copy = self.NetFull
        DelNodes = ringo.ConstructTIntV()
        DelNodes.Add(0)
        ringo.DelNodes(Graph_Copy, DelNodes)
        for node in DelNodes:
            self.assertFalse(Graph_Copy.IsNode(node))

    def test_DelZeroDegNodes(self):
        # Directed Graph
        ringo.DelZeroDegNodes(self.DirGraphZeroDegree)
        for NI in self.DirGraphZeroDegree.Nodes():
            self.assertNotEqual(0, NI.GetOutDeg() + NI.GetInDeg())

        # Undirected Graph
        ringo.DelZeroDegNodes(self.UnDirGraphZeroDegree)
        for NI in self.UnDirGraphZeroDegree.Nodes():
            self.assertNotEqual(0, NI.GetOutDeg() + NI.GetInDeg())

        # Network
        ringo.DelZeroDegNodes(self.NetZeroDegree)
        for NI in self.NetZeroDegree.Nodes():
            self.assertNotEqual(0, NI.GetOutDeg() + NI.GetInDeg())

    def test_DelDegKNodes(self):
        # Directed Graph
        ringo.DelDegKNodes(self.DirGraphZeroDegree, 0, 0)
        for NI in self.DirGraphZeroDegree.Nodes():
            self.assertNotEqual(0, NI.GetOutDeg() + NI.GetInDeg())

        # Undirected Graph
        ringo.DelDegKNodes(self.UnDirGraphZeroDegree, 0, 0)
        for NI in self.UnDirGraphZeroDegree.Nodes():
            self.assertNotEqual(0, NI.GetOutDeg() + NI.GetInDeg())

        # Network
        ringo.DelDegKNodes(self.NetZeroDegree, 0, 0)
        for NI in self.NetZeroDegree.Nodes():
            self.assertNotEqual(0, NI.GetOutDeg() + NI.GetInDeg())

    def test_IsTree(self):
        # Directed Graph
        expected_results = [True, 0]
        results = ringo.IsTree(self.DirTree)
        self.assertEqual(expected_results, results)

        # Network
        expected_results = [True, 0]
        results = ringo.IsTree(self.NetTree)
        self.assertEqual(expected_results, results)

    ''' primitive type error
    def test_GetTreeRootNId(self):
        # Directed Graph
        root_id = ringo.GetTreeRootNId(self.DirTree)
        self.assertEqual(0, root_id)

        # Network
        root_id = ringo.GetTreeRootNId(self.NetTree)
        self.assertEqual(0, root_id)
    '''

    def test_GetBfsTree(self):
        start_node = 0
        follow_out = True
        follow_in = False

        # Directed Graph
        BfsTree = ringo.GetBfsTree(self.DirGraphFull, start_node, follow_out, follow_in)
        self.assertEqual(self.num_nodes - 1, BfsTree.GetEdges())
        for end_node in range(1, self.num_nodes-1):
            self.assertTrue(BfsTree.IsEdge(start_node, end_node))

        # Undirected Graph
        BfsTree = ringo.GetBfsTree(self.UnDirGraphFull, start_node, follow_out, follow_in)
        self.assertEqual(self.num_nodes - 1, BfsTree.GetEdges())
        for end_node in range(1, self.num_nodes-1):
            self.assertTrue(BfsTree.IsEdge(start_node, end_node))

        # Network
        BfsTree = ringo.GetBfsTree(self.NetFull, start_node, follow_out, follow_in)
        self.assertEqual(self.num_nodes - 1, BfsTree.GetEdges())
        for end_node in range(1, self.num_nodes-1):
            self.assertTrue(BfsTree.IsEdge(start_node, end_node))

    def test_GetSubTreeSz(self):
        # Directed Graph
        results = ringo.GetSubTreeSz(self.DirTree, 0, True, True)
        exp_results = [40, 40, 3]
        self.assertEqual(exp_results, results)

        # Undirected Graph
        results = ringo.GetSubTreeSz(self.UnDirTree, 0, True, True)
        exp_results = [40, 40, 3]
        self.assertEqual(exp_results, results)

        # Network
        results = ringo.GetSubTreeSz(self.NetTree, 0, True, True)
        exp_results = [40, 40, 3]
        self.assertEqual(exp_results, results)

    ''' primitive types
    def test_GetNodesAtHop(self):
        # Directed Graph
        NodeVec, num_nodes = ringo.GetNodesAtHop(self.DirGraphStar, 0, 1, True)
        self.assertEqual(self.num_nodes-1, num_nodes)

        # Undirected Graph
        NodeVec, num_nodes = ringo.GetNodesAtHop(self.UnDirGraphStar, 0, 1, False)
        self.assertEqual(self.num_nodes-1, num_nodes)

        # Network
        NodeVec, num_nodes = ringo.GetNodesAtHop(self.NetStar, 0, 1, True)
        self.assertEqual(self.num_nodes-1, num_nodes)

    def test_GetNodesAtHops(self):
        # Directed Graph
        HopVec, num_hops = ringo.GetNodesAtHops(self.DirGraphStar, 0, True)
        self.assertEqual(2, num_hops)
        for pair in HopVec:
            if pair.Val1() == 0:
                self.assertEqual(1, pair.Val2())
            else:
                self.assertEqual(1, pair.Val1())
                self.assertEqual(self.num_nodes-1, pair.Val2())

        # Undirected Graph
        HopVec, num_hops = ringo.GetNodesAtHops(self.UnDirGraphStar, 0, False)
        self.assertEqual(2, num_hops)
        for pair in HopVec:
            if pair.Val1() == 0:
                self.assertEqual(1, pair.Val2())
            else:
                self.assertEqual(1, pair.Val1())
                self.assertEqual(self.num_nodes-1, pair.Val2())

        # Network
        HopVec, num_hops = ringo.GetNodesAtHops(self.NetStar, 0, True)
        self.assertEqual(2, num_hops)
        for pair in HopVec:
            if pair.Val1() == 0:
                self.assertEqual(1, pair.Val2())
            else:
                self.assertEqual(1, pair.Val1())
                self.assertEqual(self.num_nodes-1, pair.Val2())
		'''

    def test_GetDegreeCentr(self):
        # Undirected Graph
        degree_center = ringo.GetDegreeCentr(self.UnDirGraphStar, 0)
        self.assertEqual(1, degree_center)

    def test_GetFarnessCentr(self):
        # Undirected Graph
        farness_center = ringo.GetFarnessCentr(self.UnDirGraphStar, 0)
        self.assertEqual(1, farness_center)

    def test_GetClosenessCentr(self):
        # Undirected Graph
        closeness_center = ringo.GetClosenessCentr(self.UnDirGraphStar, 0)
        self.assertEqual(1, closeness_center)

    def test_GetEigenVectorCentr(self):
				''' 'TIntFltH' object has no attribute '__getitem__'
        # Undirected Graph
        EigenVec = ringo.GetEigenVectorCentr(self.UnDirGraphStar)
        for item in EigenVec:
            self.assertTrue(0 < EigenVec[item])
				'''

    def test_GetNodeEcc(self):
        # Directed Graph
        node_ecc = ringo.GetNodeEcc(self.DirGraphStar, 0, True)
        self.assertEqual(1, node_ecc)

        # Undirected Graph
        node_ecc = ringo.GetNodeEcc(self.UnDirGraphStar, 0, False)
        self.assertEqual(1, node_ecc)

        # Network
        node_ecc = ringo.GetNodeEcc(self.NetStar, 0, True)
        self.assertEqual(1, node_ecc)

    def test_GetHits(self):
        ''' 'TIntFltH' object has no attribute '__getitem__'
        # Directed Graph
        NIdHubH, NIdAuthH = ringo.GetHits(self.DirGraphFull)
        value = NIdHubH.GetDat(0)
        for item in NIdHubH:
            self.assertEqual(value, NIdHubH[item])
        value = NIdAuthH.GetDat(0)
        for item in NIdAuthH:
            self.assertEqual(value, NIdAuthH[item])

        # Undirected Graph
        NIdHubH = ringo.ConstructTIntFltH()
        NIdAuthH = ringo.ConstructTIntFltH()
        ringo.GetHits(self.UnDirGraphFull, NIdHubH, NIdAuthH)
        value = NIdHubH.GetDat(0)
        for item in NIdHubH:
            self.assertEqual(value, NIdHubH[item])
        value = NIdAuthH.GetDat(0)
        for item in NIdAuthH:
            self.assertEqual(value, NIdAuthH[item])

        # Network
        NIdHubH = ringo.ConstructTIntFltH()
        NIdAuthH = ringo.ConstructTIntFltH()
        ringo.GetHits(self.NetFull, NIdHubH, NIdAuthH)
        value = NIdHubH.GetDat(0)
        for item in NIdHubH:
            self.assertEqual(value, NIdHubH[item])
        value = NIdAuthH.GetDat(0)
        for item in NIdAuthH:
            self.assertEqual(value, NIdAuthH[item])
        '''

    ''' primitive type
    def test_CommunityGirvanNewman(self):
        exp_val = 0.010151451527112903
        Graph = ringo.GenPrefAttach(100, 10)
        Vec, act_val = ringo.CommunityGirvanNewman(Graph)
        self.assertAlmostEqual(exp_val, act_val)

    def test_CommunityCNM(self):
        gnutellaUndir = ringo.ConvertGraph(ringo.PUNGraph, self.gnutella)
        Vcc, modularity = ringo.CommunityCNM(gnutellaUndir)
        self.assertAlmostEqual(0.4647213330572384, modularity)
		'''

    def test_GetModularity(self):
        V = ringo.ConstructTIntV()
        for i in range(5):
            V.Add(i)

        val = ringo.GetModularity(self.DirGraphFull, V)
        self.assertAlmostEqual(0.04861111111111111, val)

        val = ringo.GetModularity(self.UnDirGraphFull, V)
        self.assertAlmostEqual(-0.027777777777777776, val)

        val = ringo.GetModularity(self.NetFull, V)
        self.assertAlmostEqual(0.04861111111111111, val)

    def test_GetEdgesInOut(self):
        V = ringo.ConstructTIntV()
        V.Add(0)

        # Directed Graph
        result = ringo.GetEdgesInOut(self.DirGraphFull, V)
        exp_results = [0, 9]
        self.assertEqual(exp_results, result)

        # Undirected Graph
        result = ringo.GetEdgesInOut(self.UnDirGraphFull, V)
        exp_results = [0, 9]
        self.assertEqual(exp_results, result)

        # Network
        result = ringo.GetEdgesInOut(self.NetFull, V)
        exp_results = [0, 9]
        self.assertEqual(exp_results, result)

    def test_GetBiConSzCnt(self):
        # Undirected Graph
        szCntV = ringo.GetBiConSzCnt(self.UnDirGraphFull)
        for item in szCntV:
            self.assertEqual(item.GetVal1(), self.num_nodes)
            self.assertEqual(item.GetVal2(), 1)

    def test_GetBiCon(self):
        # Undirected Graph
        CnComs = ringo.GetBiCon(self.UnDirGraphFull)
        nodeId = 0
        for CnCom in CnComs:
            for node in CnCom:
              self.assertEqual(nodeId, node)
              nodeId += 1 

    def test_GetEdgeBridges(self):
        # Undirected Graph
        edges = ringo.GetEdgeBridges(self.UnDirGraphStar)
        count = 0
        for edge in edges:
            self.assertEqual(0, edge.GetVal1())
            self.assertNotEqual(0, edge.GetVal2())
            count+=1
        self.assertEqual(9, count)

    def test_Get1CnCom(self):
        # Undirected Graph
        components = ringo.Get1CnCom(self.UnDirGraphStar)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes-1, comp_size)

    def test_GetMxBiCon(self):
        # Directed Graph
        Graph = ringo.GetMxBiCon(self.DirGraphFull)
        self.assertEqual(self.DirGraphFull.GetNodes(), Graph.GetNodes())
        self.assertEqual(self.DirGraphFull.GetEdges(), Graph.GetEdges())
        self.assertEqual(type(self.DirGraphFull), type(Graph))

        # Undirected Graph
        Graph = ringo.GetMxBiCon(self.UnDirGraphFull)
        self.assertEqual(self.UnDirGraphFull.GetNodes(), Graph.GetNodes())
        self.assertEqual(self.UnDirGraphFull.GetEdges(), Graph.GetEdges())
        self.assertEqual(type(self.UnDirGraphFull), type(Graph))

        # Network
        Graph = ringo.GetMxBiCon(self.NetFull)
        self.assertEqual(self.NetFull.GetNodes(), Graph.GetNodes())
        self.assertEqual(self.NetFull.GetEdges(), Graph.GetEdges())
        self.assertEqual(type(Graph), type(self.NetFull))

    def test_GetNodeWcc(self):
        # Directed Graph
        component = ringo.GetNodeWcc(self.DirGraphStar, 1)
        sumNodes = 0
        for node in component:
            sumNodes += node
        self.assertEqual((self.num_nodes - 1) * self.num_nodes / 2, sumNodes)

        # Undirected Graph
        component = ringo.GetNodeWcc(self.UnDirGraphStar, 1)
        sumNodes = 0
        for node in component:
            sumNodes += node
        self.assertEqual((self.num_nodes - 1) * self.num_nodes / 2, sumNodes)

        # Network
        component = ringo.GetNodeWcc(self.NetStar, 1)
        sumNodes = 0
        for node in component:
            sumNodes += node
        self.assertEqual((self.num_nodes - 1) * self.num_nodes / 2, sumNodes)

    def test_isConnected(self):
        # Directed Graph
        self.assertTrue(ringo.IsConnected(self.DirGraphStar))

        # Undirected Graph
        self.assertTrue(ringo.IsConnected(self.UnDirGraphStar))

        # Network
        self.assertTrue(ringo.IsConnected(self.NetStar))

    def test_isWeaklyConn(self):
        # Directed Graph
        self.assertTrue(ringo.IsWeaklyConn(self.DirGraphStar))

        # Undirected Graph
        self.assertTrue(ringo.IsWeaklyConn(self.UnDirGraphStar))

        # Network
        self.assertTrue(ringo.IsWeaklyConn(self.NetStar))

    def test_GetWccSzCnt(self):
        # Directed Graph
        counts = ringo.GetWccSzCnt(self.DirGraphStar)
        for pair in counts:
            self.assertEqual(self.num_nodes, pair.GetVal1())
            self.assertEqual(1, pair.GetVal2())

        # Undirected Graph
        counts = ringo.GetWccSzCnt(self.UnDirGraphStar)
        for pair in counts:
            self.assertEqual(self.num_nodes, pair.GetVal1())
            self.assertEqual(1, pair.GetVal2())

        # Network
        counts = ringo.GetWccSzCnt(self.NetStar)
        for pair in counts:
            self.assertEqual(self.num_nodes, pair.GetVal1())
            self.assertEqual(1, pair.GetVal2())

    def test_GetWccs(self):
        # Directed Graph
        components = ringo.GetWccs(self.DirGraphStar)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes, comp_size)

        # Undirected Graph
        components = ringo.GetWccs(self.UnDirGraphStar)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes, comp_size)

        # Network
        components = ringo.GetWccs(self.NetStar)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes, comp_size)

    def test_GetSccSzCnt(self):
         # Directed Graph
        SccSzCnt = ringo.GetSccSzCnt(self.DirGraphFull)
        for pair in SccSzCnt:
            self.assertEqual(self.num_nodes, pair.GetVal1())
            self.assertEqual(1, pair.GetVal2())

        # Undirected Graph
        SccSzCnt = ringo.GetSccSzCnt(self.UnDirGraphFull)
        for pair in SccSzCnt:
            self.assertEqual(self.num_nodes, pair.GetVal1())
            self.assertEqual(1, pair.GetVal2())

        # Network
        SccSzCnt = ringo.GetSccSzCnt(self.NetFull)
        for pair in SccSzCnt:
            self.assertEqual(self.num_nodes, pair.GetVal1())
            self.assertEqual(1, pair.GetVal2())

    def test_GetSccs(self):
        # Directed Graph
        components = ringo.GetSccs(self.DirGraphFull)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes, comp_size)

        # Undirected Graph
        components = ringo.GetSccs(self.UnDirGraphFull)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes, comp_size)

        # Network
        components = ringo.GetSccs(self.NetFull)
        num_comp = 0
        comp_size = 0
        for comp in components:
            num_comp += 1
            for node in comp:
                comp_size += 1
        self.assertEqual(1, num_comp)
        self.assertEqual(self.num_nodes, comp_size)

    def test_GetMxWccSz(self):
        # Directed Graph
        sz = ringo.GetMxWccSz(self.DirGraphStar)
        self.assertEqual(1, sz)

        # Undirected Graph
        sz = ringo.GetMxWccSz(self.UnDirGraphStar)
        self.assertEqual(1, sz)

        # Network
        sz = ringo.GetMxWccSz(self.NetStar)
        self.assertEqual(1, sz)

    def test_GetMxSccSz(self):
        # Directed Graph
        sz = ringo.GetMxSccSz(self.DirGraphStar)
        self.assertEqual(1.0/self.num_nodes, sz)

        # Undirected Graph
        sz = ringo.GetMxSccSz(self.UnDirGraphStar)
        self.assertEqual(1, sz)

        # Network
        sz = ringo.GetMxSccSz(self.NetStar)
        self.assertEqual(1.0/self.num_nodes, sz)

    def test_GetMxWcc(self):
        # Directed Graph
        subgraph = ringo.GetMxWcc(self.DirGraphStar)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Undirected Graph
        subgraph = ringo.GetMxWcc(self.UnDirGraphStar)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Network
        subgraph = ringo.GetMxWcc(self.NetStar)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

    def test_GetMxScc(self):
        # Directed Graph
        subgraph = ringo.GetMxScc(self.DirGraphFull)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Undirected Graph
        subgraph = ringo.GetMxScc(self.UnDirGraphFull)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Network
        subgraph = ringo.GetMxScc(self.NetFull)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

    def test_GetMxBiCon(self):
        # Directed Graph
        subgraph = ringo.GetMxBiCon(self.DirGraphFull)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Undirected Graph
        subgraph = ringo.GetMxBiCon(self.UnDirGraphFull)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Network
        subgraph = ringo.GetMxBiCon(self.NetFull)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(subgraph.IsNode(node.GetId()))
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(subgraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

    def test_PrintInfo(self):
        ringo.PrintInfo(self.DirGraphFull, "description", "test.txt")
        self.checkPrintInfoOutput("test.txt", ["description", '10', '90', '0', '0', '0', '10'])
        os.system('rm test.txt')

        ringo.PrintInfo(self.UnDirGraphFull, "description", "test.txt")
        self.checkPrintInfoOutput("test.txt", ["description", '10', '45', '0', '0', '0', '10'])
        os.system('rm test.txt')

        ringo.PrintInfo(self.NetFull, "description", "test.txt")
        self.checkPrintInfoOutput("test.txt", ["description", '10', '90', '0', '0', '0', '10'])
        os.system('rm test.txt')

    ''' primitive type
    def test_GetKCoreNodes(self):
        # Directed Graph
        CoreN, result = ringo.GetKCoreNodes(self.DirGraphStar)
        self.assertEqual(2, result)

        # Undirected Graph
        CoreN, result = ringo.GetKCoreNodes(self.UnDirGraphStar)
        self.assertEqual(2, result)

        # Network
        CoreN, result = ringo.GetKCoreNodes(self.NetStar)
        self.assertEqual(2, result)

    def test_GetKCoreEdges(self):
        # Directed Graph
        CoreN, result = ringo.GetKCoreEdges(self.DirGraphStar)
        self.assertEqual(2, result)

        # Undirected Graph
        CoreN, result = ringo.GetKCoreEdges(self.UnDirGraphStar)
        self.assertEqual(2, result)

        # Network
        CoreN, result = ringo.GetKCoreEdges(self.NetStar)
        self.assertEqual(2, result)
		'''

    def test_GenDegSeq(self):
        DegSeqV = ringo.ConstructTIntV()
        DegSeqV.Add(3)
        DegSeqV.Add(2)
        DegSeqV.Add(1)
        DegSeqV.Add(1)
        DegSeqV.Add(1)
        Graph = ringo.GenDegSeq(DegSeqV)
        count = 0
        for n in Graph.Nodes():
            count += 1
        self.assertEqual(5, count)
        count = [0, 0, 0, 0, 0]
        for node in Graph.Nodes():
            count[node.GetId()] = node.GetInDeg()
        self.assertEqual(3, count[0])
        self.assertEqual(2, count[1])
        self.assertEqual(1, count[2])
        self.assertEqual(1, count[3])
        self.assertEqual(1, count[4])

    def test_GenRewire(self):
        Rewired = ringo.GenRewire(self.UnDirRand)
        for node in self.UnDirRand.Nodes():
            for nodeR in Rewired.Nodes():
                if node.GetId() == nodeR.GetId():
                    self.assertEqual(node.GetOutDeg()+node.GetInDeg(), nodeR.GetOutDeg()+nodeR.GetInDeg())

    def test_GenPrefAttach(self):
        Graph = ringo.GenPrefAttach(100, 10)
        for node in Graph.Nodes():
            self.assertTrue(node.GetOutDeg() >= 10)
        self.assertEqual(100, Graph.GetNodes())

    def test_GenGeoPrefAttach(self):
        Graph = ringo.GenGeoPrefAttach(100, 10, 0.25)
        for node in Graph.Nodes():
            self.assertTrue(node.GetOutDeg() + node.GetInDeg() >= 10)
        self.assertEqual(100, Graph.GetNodes())

    def test_GenForestFire(self):
        Graph = ringo.GenForestFire(100, 0.5, 0.5)
        self.assertEqual(100, Graph.GetNodes())

    def test_GenRMat(self):
        Graph = ringo.GenRMat(10, 20, 0.25, 0.25, 0.25)
        self.assertEqual(10, Graph.GetNodes())
        self.assertEqual(20, Graph.GetEdges())

    def test_GenRMatEpinions(self):
        Graph = ringo.GenRMatEpinions()
        expected_nodes = 75888
        expected_edges = 508837
        self.assertEqual(expected_nodes, Graph.GetNodes())
        self.assertEqual(expected_edges, Graph.GetEdges())

    def test_GenStar(self):
        # Directed Graph
        Graph = self.DirGraphStar
        for node in Graph.Nodes():
            if node.GetId() == 0:
                self.assertEqual(self.num_nodes-1, node.GetOutDeg())
                self.assertEqual(0, node.GetInDeg())
            else:
                self.assertEqual(0, node.GetOutDeg())
                self.assertEqual(1, node.GetInDeg())

        # Undirected Graph
        Graph = self.UnDirGraphStar
        for node in Graph.Nodes():
            if node.GetId() == 0:
                self.assertEqual(self.num_nodes-1, node.GetOutDeg())
                self.assertEqual(self.num_nodes-1, node.GetInDeg())
            else:
                self.assertEqual(1, node.GetOutDeg())
                self.assertEqual(1, node.GetInDeg())

        # Network
        Graph = self.NetStar
        for node in Graph.Nodes():
            if node.GetId() == 0:
                self.assertEqual(self.num_nodes-1, node.GetOutDeg())
                self.assertEqual(0, node.GetInDeg())
            else:
                self.assertEqual(0, node.GetOutDeg())
                self.assertEqual(1, node.GetInDeg())

    def test_GenTree(self):
        # Directed Graph
        Graph = ringo.GenTree(ringo.PNGraph, 3, 3, True, False)
        for node in Graph.Nodes():
            self.assertTrue(node.GetDeg() == 4 or (node.GetDeg() == 3 and node.GetId() == 0) or node.GetDeg() == 1)

        # Undirected Graph
        Graph = ringo.GenTree(ringo.PUNGraph, 3, 3, False, False)
        for node in Graph.Nodes():
           self.assertTrue(node.GetDeg() == 4 or (node.GetDeg() == 3 and node.GetId() == 0) or node.GetDeg() == 1)

        # Network
        Graph = ringo.GenTree(ringo.PNEANet, 3, 3, True, False)
        for node in Graph.Nodes():
            self.assertTrue(node.GetDeg() == 4 or (node.GetDeg() == 3 and node.GetId() == 0) or node.GetDeg() == 1)

    def test_GenBaraHierar(self):
        expected_nodes = 625
        expected_edges = 1976

        # Directed Graph
        Graph = ringo.GenBaraHierar(ringo.PNGraph, 3, True)
        self.assertEqual(expected_nodes, Graph.GetNodes())
        self.assertEqual(expected_edges, Graph.GetEdges())

        # Directed Graph
        Graph = ringo.GenBaraHierar(ringo.PUNGraph, 3, True)
        self.assertEqual(expected_nodes, Graph.GetNodes())
        self.assertEqual(expected_edges, Graph.GetEdges())

        # Directed Graph
        Graph = ringo.GenBaraHierar(ringo.PNEANet, 3, True)
        self.assertEqual(expected_nodes, Graph.GetNodes())
        self.assertEqual(expected_edges, Graph.GetEdges())

    def test_LoadDyNet(self):
        Gout = ringo.GenRndGnm(ringo.PNGraph, 100, 1000)
        fname = "test.xml"
        with open(fname, "w") as f:
            f.write("<network>\n")

            for EI in Gout.Edges():
                src = EI.GetSrcNId()
                dst = EI.GetDstNId()
                f.write("\t<link source='" + str(src) + "' target='" + str(dst) + "'/> \n")

            f.write("</network>\n")

        Gin = ringo.LoadDyNet(fname)

        self.assertTrue(Gin.GetNodes() == Gout.GetNodes())
        self.assertTrue(Gin.GetEdges() == Gout.GetEdges())
        os.system('rm ' + fname)

    def test_LoadConnList(self):
        fname = "test.txt"
        with open(fname, "w") as f:
            for i in range(10):
                line = str(i)
                for j in range(10):
                    if j != i:
                        line += " " + str(j)
                f.write(line + "\n")

        # Directed Graph
        Graph = ringo.LoadConnList(ringo.PNGraph, fname)
        for i in range(10):
            for j in range(10):
                if i != j:
                    self.assertTrue(Graph.IsEdge(i, j))
                else:
                    self.assertFalse(Graph.IsEdge(i, j))

        # Undirected Graph
        Graph = ringo.LoadConnList(ringo.PUNGraph, fname)
        for i in range(10):
            for j in range(10):
                if i != j:
                    self.assertTrue(Graph.IsEdge(i, j))
                else:
                    self.assertFalse(Graph.IsEdge(i, j))

        # Network
        Graph = ringo.LoadConnList(ringo.PNEANet, fname)
        for i in range(10):
            for j in range(10):
                if i != j:
                    self.assertTrue(Graph.IsEdge(i, j))
                else:
                    self.assertFalse(Graph.IsEdge(i, j))

        os.system('rm ' + fname)

    def test_LoadPajek(self):
        fname = "example.paj"
        output = open(fname, "w")
        output.write('*Vertices      9\n')
        output.write('1 "1"    0.3034    0.7561\n')
        output.write('2 "2"    0.4565    0.6039\n')
        output.write('3 "3"    0.4887    0.8188\n')
        output.write('*Arcs\n')
        output.write('*Edges\n')
        output.write('    1      2       1\n')
        output.write('    1      3       1\n')
        output.write('    2      3       1\n')
        output.close()

        # Directed Graph
        Graph = ringo.LoadPajek(ringo.PNGraph, fname)
        count = 1
        for node in Graph.Nodes():
            self.assertEqual(count, node.GetId())
            count += 1

        # Undirected Graph
        Graph = ringo.LoadPajek(ringo.PUNGraph, fname)
        count = 1
        for node in Graph.Nodes():
            self.assertEqual(count, node.GetId())
            count += 1

        # Network
        Graph = ringo.LoadPajek(ringo.PNGraph, fname)
        count = 1
        for node in Graph.Nodes():
            self.assertEqual(count, node.GetId())
            count += 1

        os.system('rm ' + fname)

    def test_SaveEdgeList(self):
        ''' Terminate called after throwing an instance of TPt<TExcept>
        # Directed Graph
        fname = "mygraph.txt"
        ringo.SaveEdgeList(self.DirGraphFull, fname)
        exp_hash = 'd26278f1b4d13aac3c22763f937a30d3'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        ringo.SaveEdgeList(self.UnDirGraphFull, fname)
        exp_hash = 'c767b54d9d1c607c791d895817b9b758'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        ringo.SaveEdgeList(self.NetFull, fname)
        exp_hash = 'd26278f1b4d13aac3c22763f937a30d3'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)
        '''

    def test_SaveMatlabSparseMtx(self):
        # Directed Graph
        fname = "mygraph.txt"
        ringo.SaveMatlabSparseMtx(self.DirGraphFull, fname)
        exp_hash = 'a0e90dc5e7e3d9383a4af049d4dafee2'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        ringo.SaveMatlabSparseMtx(self.UnDirGraphFull, fname)
        exp_hash = '28a9ccb0bf7c71de564fac9d071fb704'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        ringo.SaveMatlabSparseMtx(self.NetFull, fname)
        exp_hash = 'a0e90dc5e7e3d9383a4af049d4dafee2'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_GetSngVals(self):
        SngVals = 4
        SngValV = ringo.GetSngVals(self.DirGraphFull, SngVals)
        count = 0
        for item in SngValV:
            if count == 0:
                self.assertAlmostEqual(self.num_nodes-1, item)
            else:
                self.assertAlmostEqual(1, item)
            count += 1

    def test_GetEigVals(self):
        Graph = ringo.GenStar(ringo.PUNGraph, 50)
        NumEigVals = 2
        EigValV = ringo.GetEigVals(Graph, NumEigVals)
        count = 0
        for item in EigValV:
            if count == 0:
                self.assertAlmostEqual(7.0, item)
            else:
                self.assertAlmostEqual(-7.0, item)
            count += 1
        self.assertEqual(2, count)

    ''' attribute error
    def test_GetInvParticipRate(self):
        Graph = ringo.TUNGraph.New()
        Graph.AddNode(1)
        Graph.AddNode(2)
        Graph.AddNode(3)
        Graph.AddNode(4)
        Graph.AddNode(5)
        Graph.AddNode(6)
        Graph.AddEdge(1, 2)
        Graph.AddEdge(2, 3)
        Graph.AddEdge(3, 5)
        Graph.AddEdge(4, 6)
        Graph.AddEdge(4, 1)

        expected = [[-1.246980, 0.214286],[0.445042, 0.214286],[1.801938, 0.214286]]
        EigValIprV = ringo.GetInvParticipRat(Graph, 10, 1000)
        count = 0
        for x in EigValIprV:
            self.assertAlmostEqual(expected[count][0], x.GetVal1(), 5)
            self.assertAlmostEqual(expected[count][1], x.GetVal2(), 5)
            count += 1
		'''
    def test_GetKCore(self):
        # Directed Graph
        k = self.num_nodes - 1
        KCore = ringo.GetKCore(self.DirGraphFull, k)
        self.assertEqual(self.num_nodes, KCore.GetNodes())

        # Undirected Graph
        k = self.num_nodes - 1
        KCore = ringo.GetKCore(self.UnDirGraphFull, k)
        self.assertEqual(self.num_nodes, KCore.GetNodes())

        # Network
        k = self.num_nodes - 1
        KCore = ringo.GetKCore(self.NetFull, k)
        self.assertEqual(self.num_nodes, KCore.GetNodes())

    def test_PlotEigValRank(self):
        Graph = ringo.GenStar(ringo.PUNGraph, 20)
        NumEigVals = 2
        fname = 'test'
        desc = 'test'
        plt = 'eigVal.' + fname + '.plt'
        png = 'eigVal.' + fname + '.png'
        tab = 'eigVal.' + fname + '.tab'
        ringo.PlotEigValRank(Graph, NumEigVals, fname, desc)

        self.checkPlotHash(plt, 'ef72edda8cb99b77d91d7bbba5d0602c')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '88e8150cca4d8b102e69e48f4f75bbc8')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '74c9e40a9c5254c36f3808524f42b3d8')
        os.system('rm ' + tab)

    def test_PlotEigValDistr(self):
        Graph = ringo.GenStar(ringo.PUNGraph, 20)
        NumEigVals = 2
        fname = 'test'
        desc = 'test'
        plt = 'eigDistr.' + fname + '.plt'
        png = 'eigDistr.' + fname + '.png'
        tab = 'eigDistr.' + fname + '.tab'
        ringo.PlotEigValDistr(Graph, NumEigVals, fname, desc)

        self.checkPlotHash(plt, '87176190c43582a4a84af19d369fa5cd')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'a620e5ca09dd447b4229850227678056')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'e6af369e84c82eea2fc1ae422d64f171')
        os.system('rm ' + tab)

    def test_PlotInvParticipRat(self):
        Graph = self.UnDirGraphStar
        NumEigVals = 3
        TimeLimit = 5
        fname = 'test'
        desc = 'test'
        plt = 'eigIPR.' + fname + '.plt'
        png = 'eigIPR.' + fname + '.png'
        tab = 'eigIPR.' + fname + '.tab'
        ringo.PlotInvParticipRat(Graph, NumEigVals, TimeLimit, fname, desc)

        self.checkPlotHash(plt, 'dc188265d1db138f4be76f08f9db322a')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'b518c4e4a1b0af4de529961986198127')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '303939e032d64c7f1e3d201a3bb3629e')
        os.system('rm ' + tab)

    def test_PlotSngValRank(self):
        Graph = self.DirGraphFull
        SngVals = 3
        fname = 'test'
        desc = 'test'
        plt = 'sngVal.' + fname + '.plt'
        png = 'sngVal.' + fname + '.png'
        tab = 'sngVal.' + fname + '.tab'
        ringo.PlotSngValRank(Graph, SngVals, fname, desc)

        self.checkPlotHash(plt, '4386c5925a85cc716c4f37080754abb3')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'c4d688e2e38f3a7df07067ee1c92ab64')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'bc0edcc3dd69677930bb37316e3bdddf')
        os.system('rm ' + tab)

    def test_PlotSngValDistr(self):
        Graph = self.DirGraphFull
        SngVals = 3
        fname = 'test'
        desc = 'test'
        plt = 'sngDistr.' + fname + '.plt'
        png = 'sngDistr.' + fname + '.png'
        tab = 'sngDistr.' + fname + '.tab'
        ringo.PlotSngValDistr(Graph, SngVals, fname, desc)

        self.checkPlotHash(plt, '0970fd3b510846ea89a846c221112c48')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '61a7195efc4864225c38f389e89c641e')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '8683dabf0f9d787609dc1be1867f31a5')
        os.system('rm ' + tab)

    def test_PlotInDegDistr(self):
        fname = 'test'
        desc = 'test'
        plt = 'inDeg.' + fname + '.plt'
        png = 'inDeg.' + fname + '.png'
        tab = 'inDeg.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotInDegDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'd9b3e3a929cdf399e121cea2f4602d5c')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '3a7a729d393a0ba37d455c67dacd8510')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'b3fd1f8e8d03274bc4c6b7d63dda8ac6')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotInDegDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'bf2d7db2d85cb861bb6f5ca5cb79031f')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '3a7a729d393a0ba37d455c67dacd8510')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'b3fd1f8e8d03274bc4c6b7d63dda8ac6')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotInDegDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'd9b3e3a929cdf399e121cea2f4602d5c')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '3a7a729d393a0ba37d455c67dacd8510')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'b3fd1f8e8d03274bc4c6b7d63dda8ac6')
        os.system('rm ' + tab)

    def test_PlotOutDegDistr(self):
        fname = 'test'
        desc = 'test'
        plt = 'outDeg.' + fname + '.plt'
        png = 'outDeg.' + fname + '.png'
        tab = 'outDeg.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotOutDegDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'e92a163bcada36d02e15d3dc8af89adf')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '03a7e7d530235143bf3a0ad09df30d5d')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'b3fd1f8e8d03274bc4c6b7d63dda8ac6')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotOutDegDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'ff92a479ebcbefcb4243b07ddd2fc487')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '03a7e7d530235143bf3a0ad09df30d5d')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'b3fd1f8e8d03274bc4c6b7d63dda8ac6')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotOutDegDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'e92a163bcada36d02e15d3dc8af89adf')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '03a7e7d530235143bf3a0ad09df30d5d')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'b3fd1f8e8d03274bc4c6b7d63dda8ac6')
        os.system('rm ' + tab)

    def test_PlotWccDistr(self):
        fname = 'test'
        desc = 'test'
        plt = 'wcc.' + fname + '.plt'
        png = 'wcc.' + fname + '.png'
        tab = 'wcc.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotWccDistr(Graph, fname, desc)

        self.checkPlotHash(plt, '7ccee4a88626c30869d632cc50d4c743')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '3092ffd346709cbb0fb1210e39314c4c')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'ead5104c0c23279add2652356fe836e4')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotWccDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'e4650e97188f1abbf7276c36f0d3715a')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '3092ffd346709cbb0fb1210e39314c4c')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'ead5104c0c23279add2652356fe836e4')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotWccDistr(Graph, fname, desc)

        self.checkPlotHash(plt, '7ccee4a88626c30869d632cc50d4c743')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '3092ffd346709cbb0fb1210e39314c4c')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'ead5104c0c23279add2652356fe836e4')
        os.system('rm ' + tab)

    def test_PlotSccDistr(self):
        fname = 'test'
        desc = 'test'
        plt = 'scc.' + fname + '.plt'
        png = 'scc.' + fname + '.png'
        tab = 'scc.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotSccDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'f717ce0536c1170e5e4dd65c747c45f8')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '91fb4493d7a2e9fef7fc998607a94649')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'ead5104c0c23279add2652356fe836e4')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotSccDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'c73a492414e2dcf789ee0105d0bb67d9')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '91fb4493d7a2e9fef7fc998607a94649')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'ead5104c0c23279add2652356fe836e4')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotSccDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'f717ce0536c1170e5e4dd65c747c45f8')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '91fb4493d7a2e9fef7fc998607a94649')
        os.system('rm ' + png)
        self.checkPlotHash(tab, 'ead5104c0c23279add2652356fe836e4')
        os.system('rm ' + tab)

    def test_PlotClustCf(self):
        fname = 'test'
        desc = 'test'
        plt = 'ccf.' + fname + '.plt'
        png = 'ccf.' + fname + '.png'
        tab = 'ccf.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotClustCf(Graph, fname, desc)

        self.checkPlotHash(plt, '410a506a1947bb433e269906b7d5acfb')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '634a0518b0ee9db6c712ade205e089a2')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '5e08cd594354ee12d733c98ffbb888c4')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotClustCf(Graph, fname, desc)

        self.checkPlotHash(plt, 'dcb27db0f17b47fc4f5e326bc535434a')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '634a0518b0ee9db6c712ade205e089a2')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '0350d2154b877f0ae9415ea4d7e07f07')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotClustCf(Graph, fname, desc)

        self.checkPlotHash(plt, '410a506a1947bb433e269906b7d5acfb')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '634a0518b0ee9db6c712ade205e089a2')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '5e08cd594354ee12d733c98ffbb888c4')
        os.system('rm ' + tab)

    def test_PlotHops(self):
        fname = 'test'
        desc = 'test'
        plt = 'hop.' + fname + '.plt'
        png = 'hop.' + fname + '.png'
        tab = 'hop.' + fname + '.tab'
        NApprox = 1024

        # Directed Graph
        Graph = self.DirGraphFull
        isDir = True
        ringo.PlotHops(Graph, fname, desc, isDir, NApprox)

        self.assertTrue(os.path.isfile(plt))
        os.system('rm ' + plt)
        self.checkPlotHash(png, '7558cfcb4b34e02fdda090fe2ebdeb03')
        os.system('rm ' + png)
        self.assertTrue(os.path.isfile(tab))
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        isDir = False
        ringo.PlotHops(Graph, fname, desc, isDir, NApprox)

        self.assertTrue(os.path.isfile(plt))
        os.system('rm ' + plt)
        self.checkPlotHash(png, '7558cfcb4b34e02fdda090fe2ebdeb03')
        os.system('rm ' + png)
        self.assertTrue(os.path.isfile(tab))
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        isDir = True
        ringo.PlotHops(Graph, fname, desc, isDir, NApprox)

        self.assertTrue(os.path.isfile(plt))
        os.system('rm ' + plt)
        self.checkPlotHash(png, '7558cfcb4b34e02fdda090fe2ebdeb03')
        os.system('rm ' + png)
        self.assertTrue(os.path.isfile(tab))
        os.system('rm ' + tab)

    def test_PlotShortPathDistr(self):
        fname = 'test'
        desc = 'test'
        plt = 'diam.' + fname + '.plt'
        png = 'diam.' + fname + '.png'
        tab = 'diam.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotShortPathDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'a1127b6c5b3bdf9cecf0acfb8f6601a6')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'ceaaab603196866102afa52042d33b15')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '9b31a3d74e08ba09fb560dd2cfbf8e59')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotShortPathDistr(Graph, fname, desc)

        self.checkPlotHash(plt, '77122e76a58641cb3346031286c3ec63')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'ceaaab603196866102afa52042d33b15')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '9b31a3d74e08ba09fb560dd2cfbf8e59')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotShortPathDistr(Graph, fname, desc)

        self.checkPlotHash(plt, 'a1127b6c5b3bdf9cecf0acfb8f6601a6')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'ceaaab603196866102afa52042d33b15')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '9b31a3d74e08ba09fb560dd2cfbf8e59')
        os.system('rm ' + tab)

    def test_PlotKCoreNodes(self):
        fname = 'test'
        desc = 'test'
        plt = 'coreNodes.' + fname + '.plt'
        png = 'coreNodes.' + fname + '.png'
        tab = 'coreNodes.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotKCoreNodes(Graph, fname, desc)

        self.checkPlotHash(plt, '727347069c3ab8793ae7e0c88408f210')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'c4ffb2358ff82930b8832cbe1d5d3ecd')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '1b1750d5304a4f2fbb19ab8919be8e27')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotKCoreNodes(Graph, fname, desc)

        self.checkPlotHash(plt, '4642b5d2de23960e8ca5d53a819a1f78')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'c4ffb2358ff82930b8832cbe1d5d3ecd')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '6a1db7740949f594b7cc3917ec65f4d9')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotKCoreNodes(Graph, fname, desc)

        self.checkPlotHash(plt, '727347069c3ab8793ae7e0c88408f210')
        os.system('rm ' + plt)
        self.checkPlotHash(png, 'c4ffb2358ff82930b8832cbe1d5d3ecd')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '1b1750d5304a4f2fbb19ab8919be8e27')
        os.system('rm ' + tab)

    def test_PlotKCoreEdges(self):
        fname = 'test'
        desc = 'test'
        plt = 'coreEdges.' + fname + '.plt'
        png = 'coreEdges.' + fname + '.png'
        tab = 'coreEdges.' + fname + '.tab'

        # Directed Graph
        Graph = self.DirGraphFull
        ringo.PlotKCoreEdges(Graph, fname, desc)

        self.checkPlotHash(plt, '7ad35cfc8d4f8234d615fc7c98619b39')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '6fab2c397c5b4ab0b740d4a5adf4171a')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '7c22771f72c0bbe0c5ac5fa7c97928eb')
        os.system('rm ' + tab)

        # Undirected Graph
        Graph = self.UnDirGraphFull
        ringo.PlotKCoreEdges(Graph, fname, desc)

        self.checkPlotHash(plt, '25cef89279ee7ab43e841f09e54d3106')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '6fab2c397c5b4ab0b740d4a5adf4171a')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '13f4612f2cec666a421b39d18ae7afb6')
        os.system('rm ' + tab)

        # Network
        Graph = self.NetFull
        ringo.PlotKCoreEdges(Graph, fname, desc)

        self.checkPlotHash(plt, '7ad35cfc8d4f8234d615fc7c98619b39')
        os.system('rm ' + plt)
        self.checkPlotHash(png, '6fab2c397c5b4ab0b740d4a5adf4171a')
        os.system('rm ' + png)
        self.checkPlotHash(tab, '7c22771f72c0bbe0c5ac5fa7c97928eb')
        os.system('rm ' + tab)

    def test_GetESubGraph(self):
        EIdV = ringo.ConstructTIntV()
        for edge in self.NetStar.Edges():
            EIdV.Add(edge.GetId())
        ESubGraph = ringo.GetESubGraph(self.NetStar, EIdV)
        for node in self.NetStar.Nodes():
            self.assertTrue(ESubGraph.IsNode(node.GetId()))
        for edge in self.NetStar.Edges():
            self.assertTrue(ESubGraph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

    def test_ConvertGraph(self):
        # Directed to Undirected
        UnDirStar = ringo.ConvertGraph(ringo.PUNGraph, self.DirGraphStar)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(UnDirStar.IsNode(node.GetId()))
        self.assertEqual(UnDirStar.GetNodes(), self.DirGraphStar.GetNodes())
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(UnDirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(UnDirStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(UnDirStar.GetEdges(), self.DirGraphStar.GetEdges())

        # Directed to Network
        NetStar = ringo.ConvertGraph(ringo.PNEANet, self.DirGraphStar)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(NetStar.IsNode(node.GetId()))
        self.assertEqual(NetStar.GetNodes(), self.DirGraphStar.GetNodes())
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(NetStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
        self.assertEqual(NetStar.GetEdges(), self.DirGraphStar.GetEdges())

        # Undirected to Directed
        DirStar = ringo.ConvertGraph(ringo.PNGraph, self.UnDirGraphStar)
        for node in self.UnDirGraphStar.Nodes():
            self.assertTrue(DirStar.IsNode(node.GetId()))
        self.assertEqual(DirStar.GetNodes(), self.UnDirGraphStar.GetNodes())
        for edge in self.UnDirGraphStar.Edges():
            self.assertTrue(DirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(DirStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(DirStar.GetEdges(), self.UnDirGraphStar.GetEdges()*2)

        # Undirected to Network
        NetStar = ringo.ConvertGraph(ringo.PNEANet, self.UnDirGraphStar)
        for node in self.UnDirGraphStar.Nodes():
            self.assertTrue(NetStar.IsNode(node.GetId()))
        self.assertEqual(NetStar.GetNodes(), self.UnDirGraphStar.GetNodes())
        for edge in self.UnDirGraphStar.Edges():
            self.assertTrue(NetStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(NetStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(NetStar.GetEdges(), self.UnDirGraphStar.GetEdges()*2)

        # Network to Undirected
        UnDirStar = ringo.ConvertGraph(ringo.PUNGraph, self.NetStar)
        for node in self.NetStar.Nodes():
            self.assertTrue(UnDirStar.IsNode(node.GetId()))
        self.assertEqual(UnDirStar.GetNodes(), self.NetStar.GetNodes())
        for edge in self.NetStar.Edges():
            self.assertTrue(UnDirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(UnDirStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(UnDirStar.GetEdges(), self.NetStar.GetEdges())

        # Network to Directed
        DirStar = ringo.ConvertGraph(ringo.PNGraph, self.NetStar)
        for node in self.NetStar.Nodes():
            self.assertTrue(DirStar.IsNode(node.GetId()))
        self.assertEqual(DirStar.GetNodes(), self.NetStar.GetNodes())
        for edge in self.NetStar.Edges():
            self.assertTrue(DirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
        self.assertEqual(DirStar.GetEdges(), self.NetStar.GetEdges())

    ''' attribute error
    def test_ConvertSubGraph(self):
        ListNodes = ringo.ConstructTIntV()
        for x in range(self.num_nodes):
            ListNodes.Add(x)

        # Directed to Undirected
        UnDirStar = ringo.ConvertSubGraph(ringo.PUNGraph, self.DirGraphStar, ListNodes)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(UnDirStar.IsNode(node.GetId()))
        self.assertEqual(UnDirStar.GetNodes(), self.DirGraphStar.GetNodes())
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(UnDirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(UnDirStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(UnDirStar.GetEdges(), self.DirGraphStar.GetEdges())

        # Directed to Network
        NetStar = ringo.ConvertSubGraph(ringo.PNEANet, self.DirGraphStar, ListNodes)
        for node in self.DirGraphStar.Nodes():
            self.assertTrue(NetStar.IsNode(node.GetId()))
        self.assertEqual(NetStar.GetNodes(), self.DirGraphStar.GetNodes())
        for edge in self.DirGraphStar.Edges():
            self.assertTrue(NetStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
        self.assertEqual(NetStar.GetEdges(), self.DirGraphStar.GetEdges())

        # Undirected to Directed
        DirStar = ringo.ConvertSubGraph(ringo.PNGraph, self.UnDirGraphStar, ListNodes)
        for node in self.UnDirGraphStar.Nodes():
            self.assertTrue(DirStar.IsNode(node.GetId()))
        self.assertEqual(DirStar.GetNodes(), self.UnDirGraphStar.GetNodes())
        for edge in self.UnDirGraphStar.Edges():
            self.assertTrue(DirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(DirStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(DirStar.GetEdges(), self.UnDirGraphStar.GetEdges()*2)

        # Undirected to Network
        NetStar = ringo.ConvertSubGraph(ringo.PNEANet, self.UnDirGraphStar, ListNodes)
        for node in self.UnDirGraphStar.Nodes():
            self.assertTrue(NetStar.IsNode(node.GetId()))
        self.assertEqual(NetStar.GetNodes(), self.UnDirGraphStar.GetNodes())
        for edge in self.UnDirGraphStar.Edges():
            self.assertTrue(NetStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(NetStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(NetStar.GetEdges(), self.UnDirGraphStar.GetEdges()*2)

        # Network to Undirected
        UnDirStar = ringo.ConvertSubGraph(ringo.PUNGraph, self.NetStar, ListNodes)
        for node in self.NetStar.Nodes():
            self.assertTrue(UnDirStar.IsNode(node.GetId()))
        self.assertEqual(UnDirStar.GetNodes(), self.NetStar.GetNodes())
        for edge in self.NetStar.Edges():
            self.assertTrue(UnDirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(UnDirStar.IsEdge(edge.GetDstNId(), edge.GetSrcNId()))
        self.assertEqual(UnDirStar.GetEdges(), self.NetStar.GetEdges())

        # Network to Directed
        DirStar = ringo.ConvertSubGraph(ringo.PNGraph, self.NetStar, ListNodes)
        for node in self.NetStar.Nodes():
            self.assertTrue(DirStar.IsNode(node.GetId()))
        self.assertEqual(DirStar.GetNodes(), self.NetStar.GetNodes())
        for edge in self.NetStar.Edges():
            self.assertTrue(DirStar.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
        self.assertEqual(DirStar.GetEdges(), self.NetStar.GetEdges())
    '''

    def test_GetRndSubGraph(self):
        exp_nodes = 10

        # Directed Graph
        Graph = ringo.GenRndGnm(ringo.PNGraph, 100, 1000)
        subGraph = ringo.GetRndSubGraph(Graph, exp_nodes)
        self.assertEqual(exp_nodes, subGraph.GetNodes())
        for node in subGraph.Nodes():
            self.assertTrue(Graph.IsNode(node.GetId()))
        for edge in subGraph.Edges():
            self.assertTrue(Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(Graph.IsNode(edge.GetSrcNId()))
            self.assertTrue(Graph.IsNode(edge.GetDstNId()))

        # Undirected Graph
        Graph = ringo.GenRndGnm(ringo.PUNGraph, 100, 1000)
        subGraph = ringo.GetRndSubGraph(Graph, exp_nodes)
        self.assertEqual(exp_nodes, subGraph.GetNodes())
        for node in subGraph.Nodes():
            self.assertTrue(Graph.IsNode(node.GetId()))
        for edge in subGraph.Edges():
            self.assertTrue(Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(Graph.IsNode(edge.GetSrcNId()))
            self.assertTrue(Graph.IsNode(edge.GetDstNId()))

        # Directed Graph
        Graph = ringo.GenRndGnm(ringo.PNEANet, 100, 1000)
        subGraph = ringo.GetRndSubGraph(Graph, exp_nodes)
        self.assertEqual(exp_nodes, subGraph.GetNodes())
        for node in subGraph.Nodes():
            self.assertTrue(Graph.IsNode(node.GetId()))
        for edge in subGraph.Edges():
            self.assertTrue(Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))
            self.assertTrue(Graph.IsNode(edge.GetSrcNId()))
            self.assertTrue(Graph.IsNode(edge.GetDstNId()))

    def test_GetRndESubGraph(self):
        exp_edges = 10

        # Directed Graph
        Graph = ringo.GenRndGnm(ringo.PNGraph, 100, 1000)
        subGraph = ringo.GetRndESubGraph(Graph, exp_edges)
        self.assertEqual(exp_edges, subGraph.GetEdges())
        for node in subGraph.Nodes():
            self.assertTrue(Graph.IsNode(node.GetId()))
            self.assertTrue(node.GetInDeg() + node.GetOutDeg() > 0)
        for edge in subGraph.Edges():
            self.assertTrue(Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

        # Network
        Graph = ringo.GenRndGnm(ringo.PNEANet, 100, 1000)
        subGraph = ringo.GetRndESubGraph(Graph, exp_edges)
        self.assertEqual(exp_edges, subGraph.GetEdges())
        for node in subGraph.Nodes():
            self.assertTrue(Graph.IsNode(node.GetId()))
            self.assertTrue(node.GetInDeg() + node.GetOutDeg() > 0)
        for edge in subGraph.Edges():
            self.assertTrue(Graph.IsEdge(edge.GetSrcNId(), edge.GetDstNId()))

    def test_GetTriadEdges(self):
        ''' GetTriadEdges() takes exactly 3 arguments (2 given)
        # Directed Graph
        exp_triad_edges = self.DirGraphFull.GetEdges()
        act_triad_edges = ringo.GetTriadEdges(self.DirGraphFull)
        self.assertEqual(exp_triad_edges, act_triad_edges)

        # Unirected Graph
        exp_triad_edges = self.UnDirGraphFull.GetEdges()
        act_triad_edges = ringo.GetTriadEdges(self.UnDirGraphFull)
        self.assertEqual(exp_triad_edges, act_triad_edges)

        # Network
        exp_triad_edges = self.NetFull.GetEdges()
        act_triad_edges = ringo.GetTriadEdges(self.NetFull)
        self.assertEqual(exp_triad_edges, act_triad_edges)
        '''

    def test_GetTriadParticip(self):
        f = math.factorial
        exp_num_tri = f(self.num_nodes-1)/f(2)/f(self.num_nodes-3)

        # Directed Graph
        TriadCntV = ringo.GetTriadParticip(self.DirGraphFull)
        for pair in TriadCntV:
            self.assertEqual(exp_num_tri, pair.Val1())
            self.assertEqual(self.num_nodes, pair.Val2)

        # Undirected Graph
        TriadCntV = ringo.GetTriadParticip(self.UnDirGraphFull)
        for pair in TriadCntV:
            self.assertEqual(exp_num_tri, pair.Val1())
            self.assertEqual(self.num_nodes, pair.Val2)

        # Network
        TriadCntV = ringo.GetTriadParticip(self.NetFull)
        for pair in TriadCntV:
            self.assertEqual(exp_num_tri, pair.Val1())
            self.assertEqual(self.num_nodes, pair.Val2)

    ''' attribute error
    def test_CntEdgesToSet(self):
        # Directed Graph
        G = ringo.GenFull(ringo.PNGraph, 10)
        TS = ringo.ConstructTIntSet()
        val = ringo.CntEdgesToSet(G, 0, TS)
        self.assertEqual(0, val)

        # Undirected Graph
        G = ringo.GenFull(ringo.PUNGraph, 10)
        TS = ringo.ConstructTIntSet()
        val = ringo.CntEdgesToSet(G, 0, TS)
        self.assertEqual(0, val)

        # Network
        G = ringo.GenFull(ringo.PNEANet, 10)
        TS = ringo.ConstructTIntSet()
        val = ringo.CntEdgesToSet(G, 0, TS)
        self.assertEqual(0, val)
		'''

    ''' overloading
    def test_GetDegSeqV(self):
        # Directed Graph
        G = ringo.GenFull(ringo.PNGraph, 10)
        V = ringo.GetDegSeqV(G)
        for i in V:
            self.assertEqual(18, i)

        # Undirected Graph
        G = ringo.GenFull(ringo.PUNGraph, 10)
        V = ringo.GetDegSeqV(G)
        for i in V:
            self.assertEqual(9, i)

        # Network
        G = ringo.GenFull(ringo.PNEANet, 10)
        V = ringo.GetDegSeqV(G)
        for i in V:
            self.assertEqual(18, i)

    def test_GetDegSeqV2(self):
        # Directed Graph
        G = ringo.GenFull(ringo.PNGraph, 10)
        V = ringo.ConstructTIntV()
        V2 = ringo.ConstructTIntV()
        ringo.GetDegSeqV(G, V, V2)
        for i in V:
            self.assertEqual(9, i)
        for i in V2:
            self.assertEqual(9, i)

        # Undirected Graph
        G = ringo.GenFull(ringo.PUNGraph, 10)
        V = ringo.ConstructTIntV()
        V2 = ringo.ConstructTIntV()
        ringo.GetDegSeqV(G, V, V2)
        for i in V:
            self.assertEqual(9, i)
        for i in V2:
            self.assertEqual(9, i)

        # Network
        G = ringo.GenFull(ringo.PNEANet, 10)
        V = ringo.ConstructTIntV()
        V2 = ringo.ConstructTIntV()
        ringo.GetDegSeqV(G, V, V2)
        for i in V:
            self.assertEqual(9, i)
        for i in V2:
            self.assertEqual(9, i)

    def test_GetAnf(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        SrcNId = 0
        DistNbrsV = ringo.GetAnf(Graph, SrcNId, 3, False, 8192)
        self.assertEqual(3, DistNbrsV.Len())

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        SrcNId = 0
        DistNbrsV = ringo.GetAnf(Graph, SrcNId, 3, False, 8192)
        self.assertEqual(3, DistNbrsV.Len())

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        SrcNId = 0
        DistNbrsV = ringo.GetAnf(Graph, SrcNId, 3, False, 8192)
        self.assertEqual(3, DistNbrsV.Len())

    def test_GetAnf2(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        DistNbrsV = ringo.ConstructTIntFltKdV()
        ringo.GetAnf(Graph, DistNbrsV, 3, False, 8192)
        self.assertEqual(3, DistNbrsV.Len())

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        DistNbrsV = ringo.ConstructTIntFltKdV()
        ringo.GetAnf(Graph, DistNbrsV, 3, False, 8192)
        self.assertEqual(3, DistNbrsV.Len())

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        DistNbrsV = ringo.ConstructTIntFltKdV()
        ringo.GetAnf(Graph, DistNbrsV, 3, False, 8192)
        self.assertEqual(3, DistNbrsV.Len())

    def test_GetAnfEffDiam(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetAnfEffDiam(Graph, True, 0.9, 1024)
        self.assertTrue(result >= 0)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetAnfEffDiam(Graph, True, 0.9, 1024)
        self.assertTrue(result >= 0)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetAnfEffDiam(Graph, True, 0.9, 1024)
        self.assertTrue(result >= 0)

    def test_GetAnfEffDiam2(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetAnfEffDiam(Graph)
        self.assertTrue(result >= 0)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetAnfEffDiam(Graph)
        self.assertTrue(result >= 0)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetAnfEffDiam(Graph)
        self.assertTrue(result >= 0)
		'''
		
    ''' primitive type error
    def test_GetShortPath(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetShortPath(Graph, 0, 1)
        self.assertEqual(1, result)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetShortPath(Graph, 0, 1)
        self.assertEqual(1, result)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetShortPath(Graph, 0, 1)
        self.assertEqual(1, result)

    def test_GetShortPath2(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        H, result = ringo.GetShortPath(Graph, 0, H)
        self.assertEqual(1, result)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        H, result = ringo.GetShortPath(Graph, 0, H)
        self.assertEqual(1, result)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        H, result = ringo.GetShortPath(Graph, 0, H)
        self.assertEqual(1, result)
		'''

    def test_GetBfsFullDiam(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetBfsFullDiam(Graph, 10)
        self.assertEqual(1, result)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetBfsFullDiam(Graph, 10)
        self.assertEqual(1, result)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetBfsFullDiam(Graph, 10)
        self.assertEqual(1, result)

    def test_GetBfsEffDiam(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetBfsEffDiam(Graph, 10)
        self.assertAlmostEqual(0.88888888888888888888, result)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetBfsEffDiam(Graph, 10)
        self.assertAlmostEqual(0.88888888888888888888, result)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetBfsEffDiam(Graph, 10)
        self.assertAlmostEqual(0.88888888888888888888, result)

    def test_GetBetweennessCentr(self):
        '''  'TIntFltH' object has no attribute '__getitem__'
        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        Nodes, Edges = ringo.GetBetweennessCentr(Graph, 1.0)
        for node in Nodes:
            self.assertAlmostEqual(0, Nodes[node])
        for edge in Edges:
            self.assertAlmostEqual(2, Edges[edge])
        '''

    def test_GetArtPoints(self):
        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        V = ringo.GetArtPoints(Graph)
        self.assertEqual(0, V.Len())

    def test_GenRndPowerLaw(self):
        # Undirected Graph
        Graph = ringo.GenRndPowerLaw (9, 10)
        self.assertEqual(Graph.GetNodes(), 9)

    def test_GenConfModel(self):
        # Undirected Graph
        DegSeqV = ringo.ConstructTIntV()
        DegSeqV.Add(0)
        Graph = ringo.GenConfModel(DegSeqV)
        self.assertEqual(Graph.GetNodes(), 1)

    def test_GenConfModel1(self):
				''' Hanging the test for some reason.
        # Undirected Graph
        GraphIn = ringo.GenFull(ringo.PUNGraph, 10)
        Graph = ringo.GenConfModel(GraphIn)
        self.assertEqual(Graph.GetNodes(), 10)
				'''

    def test_GenSmallWorld(self):
        # Undirected Graph
        Graph = ringo.GenSmallWorld(10, 3, 0)
        self.assertEqual(Graph.GetNodes(), 10)

    def test_GenCopyModel(self):
        # Directed Graph
        Graph = ringo.GenCopyModel(20, 0.4)
        self.assertEqual(Graph.GetNodes(), 20)

    def test_GenGrid(self):
        # Directed Graph
        Graph = ringo.GenGrid(ringo.PNGraph, 2, 2)
        self.assertEqual(Graph.GetNodes(), 4)
        self.assertEqual(Graph.GetEdges(), 4)

        # Undirected Graph
        Graph = ringo.GenGrid(ringo.PUNGraph, 2, 2)
        self.assertEqual(Graph.GetNodes(), 4)
        self.assertEqual(Graph.GetEdges(), 4)

        # Network
        Graph = ringo.GenGrid(ringo.PNEANet, 2, 2)
        self.assertEqual(Graph.GetNodes(), 4)
        self.assertEqual(Graph.GetEdges(), 4)

    def test_GenFull(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 5)
        self.assertEqual(Graph.GetNodes(), 5)
        self.assertEqual(Graph.GetEdges(), 20)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 5)
        self.assertEqual(Graph.GetNodes(), 5)
        self.assertEqual(Graph.GetEdges(), 10)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 5)
        self.assertEqual(Graph.GetNodes(), 5)
        self.assertEqual(Graph.GetEdges(), 20)

    def test_GenRndGnm(self):
        # Directed Graph
        Graph = ringo.GenRndGnm(ringo.PNGraph, 100, 1000)
        self.assertEqual(Graph.GetNodes(), 100)
        self.assertEqual(Graph.GetEdges(), 1000)

        # Undirected Graph
        Graph = ringo.GenRndGnm(ringo.PUNGraph, 100, 1000)
        self.assertEqual(Graph.GetNodes(), 100)
        self.assertEqual(Graph.GetEdges(), 1000)

        # Network
        Graph = ringo.GenRndGnm(ringo.PNEANet, 100, 1000)
        self.assertEqual(Graph.GetNodes(), 100)
        self.assertEqual(Graph.GetEdges(), 1000)

    ''' attribute error
    def test_GetCmnNbrs(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetCmnNbrs(Graph, 0, 1)
        self.assertEqual(result, 8)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetCmnNbrs(Graph, 0, 1)
        self.assertEqual(result, 8)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetCmnNbrs(Graph, 0, 1)
        self.assertEqual(result, 8)

    def test_GetCmnNbrs1(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        V, result = ringo.GetCmnNbrs(Graph, 0, 1)
        self.assertEqual(result, 8)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        V, result = ringo.GetCmnNbrs(Graph, 0, 1)
        self.assertEqual(result, 8)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        V, result = ringo.GetCmnNbrs(Graph, 0, 1, V)
        self.assertEqual(result, 8)
    '''

    def test_GetNodeTriads(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetNodeTriads(Graph, 0)
        self.assertEqual(result, 36)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetNodeTriads(Graph, 0)
        self.assertEqual(result, 36)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetNodeTriads(Graph, 0)
        self.assertEqual(result, 36)

    def test_GetTriads(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetTriads(Graph)
        self.assertEqual(result, 120L)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetTriads(Graph)
        self.assertEqual(result, 120L)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetTriads(Graph)
        self.assertEqual(result, 120L)

    def test_GetClustCf(self):
				'''  error : in method 'GetClustCf_PNGraph', argument 2 of type 'int'
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetClustCf(Graph)
        self.assertAlmostEqual(result, 1.0)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetClustCf(Graph)
        self.assertAlmostEqual(result, 1.0)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetClustCf(Graph)
        self.assertAlmostEqual(result, 1.0)

    def test_GetClustCf2(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        V, result = ringo.GetClustCf(Graph)
        self.assertAlmostEqual(result, 1.0)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        V, result = ringo.GetClustCf(Graph)
        self.assertAlmostEqual(result, 1.0)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        V, result = ringo.GetClustCf(Graph)
        self.assertAlmostEqual(result, 1.0)
    '''

    def test_GetClustCf3(self):
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        result = ringo.GetClustCf(Graph, 0)
        self.assertAlmostEqual(result, 0.0)

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        result = ringo.GetClustCf(Graph, 0)
        self.assertAlmostEqual(result, 0.0)

        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        result = ringo.GetClustCf(Graph, 0)
        self.assertAlmostEqual(result, 0.0)

    ''' TIntStrH does not support indexing.
    def test_SavePajek(self):
        # Directed Graph
        fname = "mygraph.txt"
        ringo.SavePajek(self.DirGraphFull, fname)
        exp_hash = '9474d66aacad5a21ce366eb6b98eb157'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        ringo.SavePajek(self.UnDirGraphFull, fname)
        exp_hash = '7552ace478ac1b2193a91f4d2707d45d'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        ringo.SavePajek(self.NetFull, fname)
        exp_hash = '9474d66aacad5a21ce366eb6b98eb157'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_SavePajek2(self):
        # Directed Graph
        fname = "mygraph.txt"
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        ringo.SavePajek(self.DirGraphFull, fname, NIdColorH)
        exp_hash = '1d0c1618ae32a2e3e600e47d9540e2e4'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        ringo.SavePajek(self.UnDirGraphFull, fname, NIdColorH)
        exp_hash = '7a63bc4bd44d9c078e50ba2a43fc484f'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        ringo.SavePajek(self.NetFull, fname, NIdColorH)
        exp_hash = '1d0c1618ae32a2e3e600e47d9540e2e4'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_SavePajek3(self):
        # Directed Graph
        fname = "mygraph.txt"
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(100):
            NIdLabelH[i] = str(i)
        ringo.SavePajek(self.DirGraphFull, fname, NIdColorH, NIdLabelH)
        exp_hash = '1d0c1618ae32a2e3e600e47d9540e2e4'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(100):
            NIdLabelH[i] = str(i)
        ringo.SavePajek(self.UnDirGraphFull, fname, NIdColorH, NIdLabelH)
        exp_hash = '7a63bc4bd44d9c078e50ba2a43fc484f'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(100):
            NIdLabelH[i] = str(i)
        ringo.SavePajek(self.NetFull, fname, NIdColorH, NIdLabelH)
        exp_hash = '1d0c1618ae32a2e3e600e47d9540e2e4'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_SavePajek4(self):
        # Directed Graph
        fname = "mygraph.txt"
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(100):
            NIdLabelH[i] = str(i)
        EIdColorH = ringo.ConstructTIntStrH()
        for i in range(1000):
            EIdColorH[i] = "black"
        ringo.SavePajek(self.DirGraphFull, fname, NIdColorH, NIdLabelH, EIdColorH)
        exp_hash = '1d0c1618ae32a2e3e600e47d9540e2e4'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(100):
            NIdLabelH[i] = str(i)
        EIdColorH = ringo.ConstructTIntStrH()
        for i in range(1000):
            EIdColorH[i] = "black"
        ringo.SavePajek(self.UnDirGraphFull, fname, NIdColorH, NIdLabelH, EIdColorH)
        exp_hash = '7a63bc4bd44d9c078e50ba2a43fc484f'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(100):
            NIdLabelH[i] = str(i)
        EIdColorH = ringo.ConstructTIntStrH()
        for i in range(1000):
            EIdColorH[i] = "black"
        ringo.SavePajek(self.NetFull, fname, NIdColorH, NIdLabelH, EIdColorH)
        exp_hash = '22acc46e0a1a57c4f74fbacac90ebd82'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_SaveGViz(self):
        # Directed Graph
        fname = "mygraph.dot"
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        ringo.SaveGViz(self.DirGraphFull, fname, "text", True, NIdColorH)
        exp_hash = '64fe626fa482a0d45416824dc02d73a5'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        ringo.SaveGViz(self.UnDirGraphFull, fname, "text", True, NIdColorH)
        exp_hash = 'd2185ec44f908e8d10da6c6319c900a5'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        NIdColorH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdColorH[i] = "red"
        ringo.SaveGViz(self.NetFull, fname, "text", True, NIdColorH)
        exp_hash = '64fe626fa482a0d45416824dc02d73a5'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_SaveGViz2(self):
        # Directed Graph
        fname = "mygraph.dot"
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdLabelH[i] = str(i)
        ringo.SaveGViz(self.DirGraphFull, fname, "text", NIdLabelH)
        exp_hash = '260c9cfe1b5eac55a053ffcf418703e1'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdLabelH[i] = str(i)
        ringo.SaveGViz(self.UnDirGraphFull, fname, "text", NIdLabelH)
        exp_hash = 'df04d8deed65d2a537a741e3ab3e251b'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Directed Graph
        NIdLabelH = ringo.ConstructTIntStrH()
        for i in range(self.num_nodes):
            NIdLabelH[i] = str(i)
        ringo.SaveGViz(self.NetFull, fname, "text", NIdLabelH)
        exp_hash = '260c9cfe1b5eac55a053ffcf418703e1'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)
    '''

    ''' Terminate called after throwing an instance of TPt<TExcept>
    def test_LoadEdgeList(self):
        # Directed Graph
        fname = "mygraph.txt"
        ringo.SaveEdgeList(self.DirGraphFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeList(ringo.PNGraph, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes)
        os.system('rm ' + fname)

        # Undirected Graph
        ringo.SaveEdgeList(self.UnDirGraphFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeList(ringo.PUNGraph, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes/2)
        os.system('rm ' + fname)

        # Directed Graph
        ringo.SaveEdgeList(self.NetFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeList(ringo.PNEANet, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes)
        os.system('rm ' + fname)

    def test_LoadEdgeList2(self):
        # Directed Graph
        fname = "mygraph.txt"
        ringo.SaveEdgeList(self.DirGraphFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeList(ringo.PNGraph, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes)
        os.system('rm ' + fname)

        # Undirected Graph
        ringo.SaveEdgeList(self.UnDirGraphFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeList(ringo.PUNGraph, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes/2)
        os.system('rm ' + fname)

        # Directed Graph
        ringo.SaveEdgeList(self.NetFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeList(ringo.PNEANet, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes)
        os.system('rm ' + fname)

    def test_LoadEdgeListStr(self):
        # Directed Graph
        fname = "mygraph.txt"
        ringo.SaveEdgeList(self.DirGraphFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeListStr(ringo.PNGraph, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes)
        os.system('rm ' + fname)

        # Undirected Graph
        ringo.SaveEdgeList(self.UnDirGraphFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeListStr(ringo.PUNGraph, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes/2)
        os.system('rm ' + fname)

        # Directed Graph
        ringo.SaveEdgeList(self.NetFull, fname)
        self.assertTrue(os.path.isfile(fname))
        Graph = ringo.LoadEdgeListStr(ringo.PNEANet, fname, 0, 1)
        self.assertEqual(Graph.GetNodes(), self.num_nodes)
        self.assertEqual(Graph.GetEdges(), (self.num_nodes-1)*self.num_nodes)
        os.system('rm ' + fname)
    '''

    def test_GetSngVec(self):
        # Directed Graph
        val = 0.316227766017
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        LeftSV, RightSV = ringo.GetSngVec(Graph)
        for i in LeftSV:
            self.assertAlmostEqual(i, val)
        for i in RightSV:
            self.assertAlmostEqual(i, val)

    def test_LoadConnList(self):
        fname = "mygraph.txt"
        output = open(fname, "w")
        output.write('0 1 2\n')
        output.write('1 2 0\n')
        output.write('2 0 1\n')
        output.close()

        # Directed Graph
        Graph = ringo.LoadConnList(ringo.PNGraph, fname)
        self.assertEqual(Graph.GetNodes(), 3)
        self.assertEqual(Graph.GetEdges(), 6)

        # Undirected Graph
        Graph = ringo.LoadConnList(ringo.PUNGraph, fname)
        self.assertEqual(Graph.GetNodes(), 3)
        self.assertEqual(Graph.GetEdges(), 3)

        # Network
        Graph = ringo.LoadConnList(ringo.PNEANet, fname)
        self.assertEqual(Graph.GetNodes(), 3)
        self.assertEqual(Graph.GetEdges(), 6)
        os.system('rm ' + fname)

    def test_GetEigVec(self):
        # Undirected Graph
        Graph = ringo.GenRndGnm(ringo.PUNGraph, 100, 500)
        V = ringo.GetEigVec(Graph)
        self.assertEqual(V.Len(), 100)
    
    ''' attribute error
		def test_DrawGViz(self):
        # Directed Graph
        fname = "mygraph.png"
        ringo.DrawGViz(self.DirGraphFull, ringo.gvlDot, fname, "graph 1")
        self.assertTrue(os.path.isfile(fname))
        self.assertTrue(os.stat(fname).st_size > 50000)
        exp_hash = '7ac8bcf157f7d916be78a09faaf13f23'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        # OP RS 2014/05/13, disabled since it is not portable
        #self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        fname = "mygraph.png"
        ringo.DrawGViz(self.UnDirGraphFull, ringo.gvlDot, fname, "graph 1")
        self.assertTrue(os.path.isfile(fname))
        self.assertTrue(os.stat(fname).st_size > 50000)
        exp_hash = '734899b11f197b88d14d771b18011d85'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        # OP RS 2014/05/13, disabled since it is not portable
        #self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Network
        fname = "mygraph.png"
        ringo.DrawGViz(self.NetFull, ringo.gvlDot, fname, "graph 1")
        self.assertTrue(os.path.isfile(fname))
        self.assertTrue(os.stat(fname).st_size > 50000)
        exp_hash = '7ac8bcf157f7d916be78a09faaf13f23'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        # OP RS 2014/05/13, disabled since it is not portable
        #self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

    def test_DrawGViz2(self):
        # Directed Graph
        fname = "mygraph.png"
        labels = ringo.ConstructTIntStrH()
        for NI in self.DirGraphFull.Nodes():
            labels[NI.GetId()] = str(NI.GetId())
        ringo.DrawGViz(self.DirGraphFull, ringo.gvlDot, fname, "graph 1", labels)
        self.assertTrue(os.stat(fname).st_size > 50000)
        self.assertTrue(os.path.isfile(fname))
        exp_hash = 'd0fa3688dd5d9c5599222270be49805e'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        # OP RS 2014/05/13, disabled since it is not portable
        #self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Undirected Graph
        fname = "mygraph.png"
        labels = ringo.ConstructTIntStrH()
        for NI in self.UnDirGraphFull.Nodes():
            labels[NI.GetId()] = str(NI.GetId())
        ringo.DrawGViz(self.UnDirGraphFull, ringo.gvlDot, fname, "graph 1", labels)
        self.assertTrue(os.path.isfile(fname))
        self.assertTrue(os.stat(fname).st_size > 50000)
        exp_hash = '191c86413fd43f23bf1c5ce4a9972863'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        # OP RS 2014/05/13, disabled since it is not portable
        #self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)

        # Network
        fname = "mygraph.png"
        labels = ringo.ConstructTIntStrH()
        for NI in self.NetFull.Nodes():
            labels[NI.GetId()] = str(NI.GetId())
        ringo.DrawGViz(self.NetFull, ringo.gvlDot, fname, "graph 1", labels)
        self.assertTrue(os.path.isfile(fname))
        self.assertTrue(os.stat(fname).st_size > 50000)
        exp_hash = 'd0fa3688dd5d9c5599222270be49805e'
        test_hash = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        # OP RS 2014/05/13, disabled since it is not portable
        #self.assertEqual(exp_hash, test_hash)
        os.system('rm ' + fname)
    '''

    ''' attribute error
    def test_GetSubGraph(self):
        V = ringo.ConstructTIntV()
        for i in range(5):
            V.Add(i)
        # Directed Graph
        Graph = ringo.GenFull(ringo.PNGraph, 10)
        SubGraph = ringo.GetSubGraph(Graph, V)
        self.assertEqual(SubGraph.GetNodes(), 5)
        self.assertEqual(SubGraph.GetEdges(), 5 * 4)
        

        # Undirected Graph
        Graph = ringo.GenFull(ringo.PUNGraph, 10)
        SubGraph = ringo.GetSubGraph(Graph, V)
        self.assertEqual(SubGraph.GetNodes(), 5)
        self.assertEqual(SubGraph.GetEdges(), 5 * 4/2)


        # Network
        Graph = ringo.GenFull(ringo.PNEANet, 10)
        SubGraph = ringo.GetSubGraph(Graph, V)
        self.assertEqual(SubGraph.GetNodes(), 5)
        self.assertEqual(SubGraph.GetEdges(), 5 * 4)
    '''

    def test_GetNodeClustCf(self):
        ''' 'TIntFltH' object has no attribute '__getitem__'
        # Directed Graph
        H = ringo.GetNodeClustCf(self.DirGraphFull)
        for i in H:
            self.assertEqual(1.0, H[i])

        # Undirected Graph
        H = ringo.GetNodeClustCf(self.UnDirGraphFull)
        for i in H:
            self.assertEqual(1.0, H[i])

        # Network
        H = ringo.GetNodeClustCf(self.NetFull)
        for i in H:
            self.assertEqual(1.0, H[i])
        '''

    def test_ConvertESubGraph(self):
        ''' attribute error
        V = ringo.ConstructTIntV()
        for i in range(10):
            V.Add(i+1)
        # Directed Graph
        SubGraph = ringo.ConvertESubGraph(ringo.PNGraph, self.NetFull, V)
        self.assertEqual(SubGraph.GetEdges(), V.Len())

        # Undirected Graph
        SubGraph = ringo.ConvertESubGraph(ringo.PUNGraph, self.NetFull, V)
        self.assertEqual(SubGraph.GetEdges(), V.Len())

        # Network
        SubGraph = ringo.ConvertESubGraph(ringo.PNEANet, self.NetFull, V)
        self.assertEqual(SubGraph.GetEdges(), V.Len())
        '''

if __name__ == '__main__':
  unittest.main()
