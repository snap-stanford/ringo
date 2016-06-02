TModeNet
=======

.. class:: TModeNet()
           TModeNet(ModeId)
           TModeNet(Nodes, Edges)
           TModeNet(Nodes, Edges, ModeId)
           TModeNet(Graph)

   Returns a new directed multigraph with node and edge attributes that represents
   a mode in a :class:`TMMNet`.
   If no parameters are provided,
   an empty graph is created. If *Nodes* and *Edges* are specified, space
   is preallocated for *Nodes* nodes and *Edges* edges. If *Graph* is specified,
   the new graph is a copy of the input graph. *ModeId* provides the integer id
   for the mode the :class:`TModeNet` represents.

   In general, :class:`TModeNet`s should not be created directly and instead should
   be added to a multimodal network using the :class:`TMMNet` method :meth:`AddModeNet`.

   :class:`TModeNet` inherits from :class:`TNEANet` and therefore has all
   the same method. In addition, it has the following multimodal related functions:

     .. describe:: GetCrossNetNames(Names)

        Gets a list of CrossNets that have this Mode as either a source or destination type.

     .. describe:: GetNeighborsByCrossNet(NId, Name, Neighbors, isOutEId=False)

        For the given node with id *NId*, gets all the neighbors for crossnet type with
        name *Name*. If this mode is both the source and dest type, the flag *isOutEId*
        specifies direction.

     .. describe:: BegMMNI(SIn)

        Returns an iterator referring to the first node in the graph.

     .. describe:: EndMMNI(SOut)

        Returns an iterator referring to the past-the-end node in the graph.

     .. describe:: GetMMNI()

        Returns an iterator referring to the node of ID NId in the graph.


TModeNetNodeI
============

.. class:: TModeNetNodeI()

    Returns a new node iterator for :class:`TModeNet`. Normally, these
    objects are not created directly,
    but obtained via a call to the network class :class:`TModeNet` method,
    such as :meth:`BegMMNI()`, that returns a node iterator.

    :class:`TModeNetNodeI` provides the following methods:

      .. describe:: Next()

        Moves the iterator to the next node in the graph.

      .. describe:: GetId()

        Returns node ID of the current node.

      .. describe:: GetDeg()

        Returns degree of the current node, the sum of in-degree and out-degree.

      .. describe:: GetInDeg()

        Returns in-degree of the current node.

      .. describe:: GetOutDeg()

        Returns out-degree of the current node.

      .. describe:: GetInNId(NodeN)

        Returns ID of *NodeN*-th in-node (the node pointing to the current node).

      .. describe:: GetOutNId(NodeN)

        Returns ID of *NodeN*-th out-node (the node the current node points to).

      .. describe:: GetNbrNId(NodeN)

        Returns ID of *NodeN*-th neighboring node. 

      .. describe:: IsInNId(NId)

        Tests whether node with ID *NId* points to the current node.

      .. describe:: IsOutNId(NId)

        Tests whether the current node points to node with ID *NId*. 

      .. describe:: IsNbrNId(NId)

        Tests whether node with ID *NId* is a neighbor of the current node.

     .. describe:: GetCrossNetNames(Names)

        Gets a list of CrossNets that include the mode this node belongs to as either a
        source or destination type.

     .. describe:: GetNeighborsByCrossNet(Name, Neighbors, isOutEId=False)

        For the given node, gets all the neighbors for crossnet type with name *Name*. If
        this mode is both the source and dest type, the flag *isOutEId* specifies direction.



TCrossNet
=======

.. class:: TCrossNet()
           TCrossNet(SrcModeId, DstModeId, CrossNetId)
           TCrossNet(SrcModeId, DstModeId, IsDir, CrossNetId)
           TCrossNet(Graph)

   Returns a new crossnet, which consists of the edges between two different modes
   in a multimodal network. If no parameters are provided, an empty crossnet is created.
   *SrcModeId* and *DstModeId* provide the ids for the source and destination mode id.
   *IsDir* indicates whether the edges in the crossnet are directed. *CrossNetId*
   gives the id for this crossnet. If *Graph* is specified,
   the new crossnet is a copy of the input crossnet.

   A :class:`TCrossNet` should not be created directly and instead should
   be added to a multimodal network using the :class:`TMMNet` method :meth:`AddCrossNet`.

   Methods for :class:`TCrossNet` are presented in two groups. The first
   group of methods deal with graph structure which includes edges.
   The second group of methods deal with edge attributes.

   :class:`TCrossNet` provides iterators for fast traversal of edges
   and attributes.
   Iterator classes are
   :class:`TCrossNetEdgeI` for iterating over edges, and
   :class:`TCrossNetAIntI`, :class:`TCrossNetAFltI`, :class:`TCrossNetAStrI`
   for iterating over integer, float or string attributes, respectively.

   :class:`TCrossNet` methods for graph structure are the following:

     .. describe:: Save(SOut)

        Saves the crossnet to a binary stream *SOut*. 

     .. describe:: GetEdges()

        Returns the number of edges in the crossnet. 

     .. describe:: AddEdge(SrcNId, DstNId, EId=-1)

        Adds an edge with ID *EId* between node IDs *SrcNId* and *DstNId*
        to the crossnet. Returns the ID of the edge being added. If *EId* is -1,
        edge ID is automatically assigned. Throws an exception, if an edge
        with ID *EId* already exists or if either *SrcNId* or *DstNId* does
        not exist.

     .. describe:: DelEdge(EId)

        Deletes an edge with id *EId* from the crossnet.

     .. describe:: IsEdge(EId)

        Tests whether an edge with id *EId* exists in the graph. 

     .. describe:: BegEdgeI()

        Returns an edge iterator referring to the first edge in the crossnet. 

     .. describe:: EndEdgeI()

        Returns an edge iterator referring to the past-the-end edge in the crossnet.

     .. describe:: GetEdgeI(EId)

        Returns an edge iterator referring to edge with id *EId* in the crossnet.

     .. describe:: Clr()

        Deletes all edges from the graph. 

     .. describe:: GetMode1()

        Returns the id of the source mode.

     .. describe:: GetMode2()

        Returns the id of the destination mode.

     .. describe:: IsDirected()

        Returns whether edges in the crossnet are directed.

   :class:`TCrossNet` methods for edge attributes support
   attributes of different types.
   Integer, float and string attributes are implemented.
   Each attribute type has its own method for a particular task.
   Attributes are named via string names.

   :class:`TCrossNet` methods for attributes are the following:

     .. describe:: AddIntAttrE(Attr)
                   AddFltAttrE(Attr)
                   AddStrAttrE(Attr)

        Defines a new integer, float or string edge attribute, respectively.

     .. describe:: DelAttrE(Attr)

        Deletes edge attribute *Attr*.

     .. describe:: AddIntAttrDatE(EdgeI, Value, Attr)
                   AddFltAttrDatE(EdgeI, Value, Attr)
                   AddStrAttrDatE(EdgeI, Value, Attr)

        Sets the value of attribute named *Attr* for the edge referred to
        by edge iterator *EdgeI* to *Value*.
        *Value* is an integer, a float, or a string, respectively.

     .. describe:: AddIntAttrDatE(EId, Value, Attr)
                   AddFltAttrDatE(EId, Value, Attr)
                   AddStrAttrDatE(EId, Value, Attr)

        Sets the value of attribute named *Attr* for the edge with
        edge id *EId* to *Value*.
        *Value* is an integer, a float, or a string, respectively.


     .. describe:: GetIntAttrDatE(EdgeI, Attr)
                   GetFltAttrDatE(EdgeI, Attr)
                   GetStrAttrDatE(EdgeI, Attr)

        Returns the value of attribute named *Attr* for the edge referred to
        by edge iterator *EdgeI**.
        Result is an integer, a float, or a string, respectively.

     .. describe:: GetIntAttrDatE(EId, Attr)
                   GetFltAttrDatE(EId, Attr)
                   GetStrAttrDatE(EId, Attr)

        Returns the value of attribute named *Attr* for the edge with
        edge id *EId*.
        Result is an integer, a float, or a string, respectively.

     .. describe:: BegEAIntI(Attr)
                   BegEAFltI(Attr)
                   BegEAStrI(Attr)

        Returns an integer, float, or string attribute iterator, respectively,
        of the attribute named *Attr* referring to the first edge.

     .. describe:: EndEAIntI(Attr)
                   EndEAFltI(Attr)
                   EndEAStrI(Attr)

        Returns an integer, float, or string attribute iterator, respectively,
        of the attribute named *Attr* referring to the past-the-end edge.

     .. describe:: GetEAIntI(Attr, EId)
                   GetEAFltI(Attr, EId)
                   GetEAStrI(Attr, EId)

        Returns an integer, float, or string attribute iterator, respectively,
        of the attribute named *Attr* referring to the edge
        with edge ID *EId*.

     .. describe:: DelAttrDatE(EdgeI, Attr)

        Deletes the value of attribute named *Attr* for the edge referred to
        by edge iterator *EdgeI*.

     .. describe:: DelAttrDatE(EId, Attr)

        Deletes the value of attribute named *Attr* for the edge with
        edge ID *EId*.

     .. describe:: IsIntAttrDeletedE(EId, Attr)
                   IsFltAttrDeletedE(EId, Attr)
                   IsStrAttrDeletedE(EId, Attr)

        Returns whether the int, float, or string attribute, respectively 
        has been deleted.

TCrossNetEdgeI
============

.. class:: TCrossNetEdgeI()

    Returns a new edge iterator for :class:`TCrossNet`. Normally, these
    objects are not created directly,
    but obtained via a call to the graph class :class:`TCrossNet` method,
    such as :meth:`BegEdgeI()`, that returns an edge iterator.

    :class:`TCrossNetEdgeI` provides the following methods:

      .. describe:: Next()

         Moves the iterator to the next edge in the graph.

      .. describe:: GetId()

         Returns the the edge id.

      .. describe:: GetSrcNId()

         Returns the ID of the source node of the edge.

      .. describe:: GetDstNId()

         Returns the ID of the destination node of the edge.

      .. describe:: GetSrcModeId()

         Returns the ID of the source mode of the edge.

      .. describe:: GetDstModeId()

         Returns the ID of the destination mode of the edge.

      .. describe:: IsDirected()

         Returns whether the edge is directed.

TCrossNetAIntI, TCrossNetAFltI, TCrossNetAStrI
========================================

.. class:: TCrossNetAIntI()
           TCrossNetAFltI()
           TCrossNetAStrI()

    Returns a new integer, float or string attribute iterator
    for :class:`TCrossNet`. Normally, these objects are not created directly,
    but obtained via a call to the graph class :class:`TCrossNet` method,
    such as :meth:`BegEAIntI()`, which returns an integer edge iterator, or
    :meth:`BegEAFltI()`, which returns a float edge iterator.

    Attribute iterators provide the following methods:

      .. describe:: Next()

        Moves the iterator to the next node or edge in the graph.

      .. describe:: GetDat()

        Returns an attribute of the node or edge.

      .. describe:: IsDeleted()

        Returns true if the attribute has been deleted.


TNEANet
=======

.. class:: TNEANet()
           TNEANet(Nodes, Edges)
           TNEANet(Graph)

   Returns a new directed multigraph with node and edge attributes.
   If no parameters are provided,
   an empty graph is created. If *Nodes* and *Edges* are specified, space
   is preallocated for *Nodes* nodes and *Edges* edges. If *Graph* is specified,
   the new graph is a copy of the input graph.

   Nodes have IDs, which are arbitrary non-negative integers. Edges have IDs.
   There can be more than one directed edge from one source node to
   a destination node. Self loops (one per node) are allowed as well as
   multiple (parallel) edges. Nodes and edges can have attributes/data
   associated with them. The attributes can be added dynamically at runtime.
   The directed multigraph data structure is implemented using sorted
   adjacency lists. This means adding a node takes constant time, while
   adding an edge takes linear time (since adjacency list is kept sorted)
   in the node degree. Accessing arbitrary node takes constant time and
   accessing any edge takes logarithmic time in the node degree.
   The attributes are organized in a columnar store, where each attribute
   column is defined for all the nodes or edges in the network. 

   Methods for :class:`TNEANet` are presented in two groups. The first
   group of methods deal with graph structure which includes nodes and edges.
   The second group of methods deal with node and edge attributes.

   :class:`TNEANet` provides iterators for fast traversal of nodes, edges
   and attributes.
   Iterator classes are :class:`TNEANetNodeI` for iterating over nodes,
   :class:`TNEANetEdgeI` for iterating over edges, and
   :class:`TNEANetAIntI`, :class:`TNEANetAFltI`, :class:`TNEANetAStrI`
   for iterating over integer, float or string attributes, respectively.
   Attribute iterators can operate over attributes for nodes or edges.

   :class:`TNEANet` methods for graph structure are the following:

     .. describe:: New()

        Returns a pointer to a new multimodal network.

     .. describe:: Load(SIn)

        Loads the multimodal network from a binary stream *SIn* and returns a pointer to it. 

     .. describe:: Save(SOut)

        Saves the multimodal network to a binary stream *SOut*. 

     .. describe:: GetModeNets()

        Returns the number of modes in the graph. 

     .. describe:: AddModeNet(ModeName)

        Adds a mode with name *ModeName* to the multimodal network. Returns the id
        for the mode.

     .. describe:: DelModeNet(ModeId)
                   DelModeNet(ModeName)

        Deletes the mode with id *ModeId* or name *ModeName*, respectively, from the
        multimodal network. 

     .. describe:: BegModeNetI()

        Returns a mode iterator referring to the first mode in the graph. 

     .. describe:: EndModeNetI()

        Returns a mode iterator referring to the past-the-end mode in the graph.

     .. describe:: GetModeNetI(MId)

        Returns a mode iterator referring to the mode with ID *MId* in the graph. 

     .. describe:: GetModeId(ModeName)

        Returns the id of the mode with name *ModeName*.

     .. describe:: GetModeName(ModeId)

        Returns the name of the mode with id *ModeId*.

     .. describe:: GetModeNetByName(ModeName)
                   GetModeNetById(ModeId)

        Returns a reference to the mode with name *ModeName* or id *ModeId*, respectively,
        in the multimodal network.

     .. describe:: GetCrossNets()

        Returns the number of crossnets in the graph. 

     .. describe:: AddCrossNet(ModeName1, ModeName2, CrossNetName, IsDir=True)
                   AddCrossNet(ModeId1, ModeId2, CrossNetName, IsDir=True)

        Adds a crossnet with name *CrossNetName* from the modes specified with
        the given names or ids. *IsDir* indicates whether the edges in the crossnet
        are directed.

     .. describe:: DelCrossNet(CrossId)
                   DelCrossNet(CrossName)

        Deletes the crossnet with id *CrossId* or name *CrossName*, respectively, from the
        multimodal network. 

     .. describe:: BegCrossNetI()

        Returns a crossnet iterator referring to the first crossnet in the graph. 

     .. describe:: EndCrossNetI()

        Returns a crossnet iterator referring to the past-the-end crossnet in the graph.

     .. describe:: GetCrossNetI(CId)

        Returns a crossnet iterator referring to the crossnet with ID *CId* in the graph. 

     .. describe:: GetCrossId(CrossName)

        Returns the id of the crossnet with name *CrossName*.

     .. describe:: GetCrossName(CrossId)

        Returns the name of the crossnet with id *CrossId*.

     .. describe:: GetCrossNetByName(CrossName)
                   GetCrossNetById(CrossId)

        Returns a reference to the crossnet with name *CrossName* or id *CrossId*,
        respectively, in the multimodal network.

TMMNetModeNetI
============

.. class:: TMMNetModeNetI()

    Returns a new mode iterator for :class:`TMMNet`. Normally, these
    objects are not created directly,
    but obtained via a call to the network class :class:`TMMNet` method,
    such as :meth:`BegModeNetI()`, that returns a mode iterator.

    :class:`TMMNetModeNetI` provides the following methods:

      .. describe:: Next()

        Moves the iterator to the next mode in the graph.

      .. describe:: GetModeId()

        Returns the ID of the current mode.

      .. describe:: GetModeName()

        Returns the name of the current mode.

      .. describe:: GetModeNet()

        Returns a reference to the current mode.

TMMNetCrossNetI
============

.. class:: TMMNetCrossNetI()

    Returns a new crossnet iterator for :class:`TMMNet`. Normally, these
    objects are not created directly,
    but obtained via a call to the graph class :class:`TMMNet` method,
    such as :meth:`BegCrossNetI()`, that returns an crossnet iterator.

    :class:`TMMNetCrossNetI` provides the following methods:

      .. describe:: Next()

        Moves the iterator to the next crossnet in the graph.

      .. describe:: GetCrossId()

        Returns the ID of the current crossnet.

      .. describe:: GetCrossName()

        Returns the name of the current crossnet.

      .. describe:: GetCrossNet()

        Returns a reference to the current crossnet.
