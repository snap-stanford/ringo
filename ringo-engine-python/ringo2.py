import snap
import time

"""
Decorator used to automate the registration of TTable operations
"""
def registerOp(opName):
    def decorator(func):
      def wrapper(*args, **kwargs):
          TableId = func(*args, **kwargs)
          args[0].UpdateOperation(opName, TableId, [args, kwargs])
          return TableId
      return wrapper
    return decorator

class ringo(object):
    NODE_ATTR_NAME = "__node_attr"
    EDGE_SRC_ATTR_NAME = "__edge_src_attr"
    EDGE_DST_ATTR_NAME = "__edge_dst_attr"

    dataTypes = ['int', 'float', 'string']
    def __init__(self):
        # mapping between table ids and table objects
        self.Tables = {}
        # an operation record has the form: <id (int), type (string), result table id, argument list (as used in python interface; table ids are used for table arguments), time stamp>
        self.Operations = [] 
        # mapping between a table (id) and the sequence of operation ids that led to it
        self.Lineage = {}
        # mapping between network ids and network objects
        self.Networks = {}
        # mapping between a table (id) and the ids of the networks that originated from it
        self.TableToNetworks = {}
        self.Context = snap.TTableContext()
        
    # Use case:
    # S = {'name':'string', 'age':'int', 'weight':'float'}
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv')
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv', [0,1]) if we want to load only columns 'name' and 'age'
    @registerOp('load tsv')
    def LoadTableTSV(self, Schema, InFnm, SeparatorChar = '\t', HasTitleLine = False):
        # prepare parameters to call TTable::LoadSS
        S = snap.Schema()  # How should this be written ?
        for attr in Schema:
            if Schema[attr] == 'int':
                S.Add(snap.TStrTAttrPr(attr, snap.atInt))  # tentative TTable interface syntax...
            elif Schema[attr] == 'float':
                S.Add(snap.TStrTAttrPr(attr, snap.atFlt))  # tentative TTable interface syntax...
            elif Schema[attr] == 'string':
                S.Add(snap.TStrTAttrPr(attr, snap.atStr))  # tentative TTable interface syntax...
            else:
                print "Illegal type %s for attribute %s" % (Schema[attr], attr)

        # Load input and create new TTable object
        TableId = self.__GetTableId()
        T = snap.TTable.LoadSS(str(TableId), S, InFnm, self.Context, SeparatorChar, snap.TBool(HasTitleLine))
        self.__UpdateTables(T, [], TableId)
        return TableId
        
    # USE CASE 2 OK
    @registerOp('save tsv')
    def SaveTableTSV(self, TableId, OutFnm):
        T = self.Tables[TableId]
        T.SaveSS(OutFnm)
        return TableId
    
    # UNTESTED
    @registerOp('load binary')
    def LoadTableBinary(self, InFnm):
        SIn = TSIn(InFnm)
        T = TTable.Load(SIn, Context)

        #T's internal name will not match TId - is this an issue?
        return self.__UpdateTables(T, [])

    # UNTESTED
    @registerOp('save binary')
    def SaveTableBinary(self, TableId, OutFnm):
        T = Tables[TableId]
        SOut = TSOut(OutFnm)
        T.Save(SOut)
        return TableId

    # UNTESTED
    def GetHistory(self, TableId):
        return str(Lineage[TableId]) #should discuss exact format of this

    # UNTESTED
    @registerOp('add label')
    def AddLabel(self, TableId, Attr, Label):
        T = Tables[TableId]
        T.AddLabel(Attr, Label)
        return TableId

    # UNTESTED
    @registerOp('unique')
    def Unique(self, TableId, GroupByAttr, InPlace = True):
        Args = (TableId, GroupByAttr, InPlace)
        if not InPlace:
            TableId = __CopyTable(TableId)
        
        T = Tables[TableId]
        T.Unique(GroupByAttr)
        return TableId

    # UNTESTED
    @registerOp('unique')
    def Unique(self, TableId, GroupByAttrs, Ordered, InPlace = True):
        Args = (TableId, GroupByAttr, NewTable)
        Attrs = TStrV()
        for Attr in GroupByAttr:
            Attrs.Add(Attr)

        if not InPlace:
            TableId = __CopyTable(TableId)

        T = Tables[TableId]
        T.Unique(Attrs, Ordered)
        return TableId

    # USE CASE 2 OK
    @registerOp('select')
    def Select(self, TableId, Predicate, InPlace = True): 
        Args = (TableId, Predicate, InPlace)
        if not InPlace:
            TableId = self.__CopyTable(TableId)
            
        # Parse predicate
        elements = Predicate.split()
        if (len(elements) != 3):
          raise NotImplementedError('Only predicates of the form "Attr1 <op> Attr2" are supported')

        T = self.Tables[TableId]
        opString = elements[1]
        try:
          op = {
            '=': snap.EQ,
            '!=': snap.NEQ,
            '<': snap.LT,
            '<=': snap.LTE,
            '>': snap.GT,
            '>=': snap.GTE,
            'in': snap.SUBSTR,
            'contains': snap.SUPERSTR
          }[opString]
        except KeyError:
          raise NotImplementedError("operator %s undefined" % opString)
        T.SelectAtomic(elements[0], elements[2], op)
        return TableId

    # UNTESTED
    @registerOp('project')
    def Project(self, TableId, Columns, InPlace = True):
        Args = (TableId, Predicate, NewTable)
        PrepCols = TStrV()
        for Col in Columns:
            PrepCols.Add(Col)

        if NewTable:
            TableId = __CopyTable(TableId)

        T = Tables[TableId]
        T.ProjectInPlace(PrepCols)
        return TableId

    # UNTESTED
    @registerOp('join')
    def Join(self, LeftTableId, RightTableId, LeftAttr, RightAttr):
        LeftT = Tables[LeftTableId]
        RightT = Tables[RightTableId]
        JoinT = LeftT.Join(LeftAttr, RightT, RightAttr)
        return self.__UpdateTables(JoinT, Lineage[LeftTableId] + Lineage[RightTableId])

    # USE CASE 1 OK
    @registerOp('join')
    def SelfJoin(self, TableId, Attr):
        T = self.Tables[TableId]
        JoinT = T.SelfJoin(Attr)

        return self.__UpdateTables(JoinT, self.Lineage[TableId])

    @registerOp('order')
    def Order(self, TableId, Attrs, Asc = False):
      T = self.Tables[TableId]
      V = snap.TStrV()
      for attr in Attrs:
        V.Add(attr)
      T.Order(V, "", snap.TBool(False), snap.TBool(Asc))
      return TableId

    # USE CASE 1 OK
    def ToGraph(self, TableId, SrcCol, DstCol):
        T = self.Tables[TableId]
        T.SetSrcCol(SrcCol)
        T.SetDstCol(DstCol)
        # TODO: How do we reset attributes when we build several graphs out of the same TTable?
        SrcV = snap.TStrV()
        DstV = snap.TStrV()
        SrcV.Add(SrcCol)
        DstV.Add(DstCol)
        T.AddSrcNodeAttr(SrcV)
        T.AddDstNodeAttr(DstV)
        return T.ToGraph(snap.FIRST)

    # UNTESTED
    def GetOpType(self, OpId):
        return Operations[OpId][1]

    # USE CASE 2 OK
    @registerOp('page rank')
    def PageRank(self, Graph, ResultAttrName = 'PageRank', AddToNetwork = False, C = 0.85, Eps = 1e-4, MaxIter = 100):
      if AddToNetwork:
        raise NotImplementedError()
      HT = snap.TIntFltH()
      snap.GetPageRank(Graph, HT, C, Eps, MaxIter)
      TableId = self.__GetTableId()
      T = snap.TTable.GetFltNodePropertyTable(Graph, str(TableId), HT, self.NODE_ATTR_NAME, ResultAttrName, self.Context)
      self.__UpdateTables(T, [], TableId)
      return TableId

    def __CopyTable(TableId):
        T = TTable.New(Tables[TableId], TId)
        CopyTableId = self.__UpdateTables(T, Lineage[TableId])
        return CopyTableId

    def __UpdateTables(self, Table, Lineage, TableId = None):
        if TableId is None:
          TableId = self.__GetTableId()
        self.Tables[TableId] = Table
        self.Lineage[TableId] = sorted(Lineage)
        return TableId

    def UpdateOperation(self, OpType, TableId, Args):
        OpId = len(self.Operations)
        Op = (OpId, OpType, TableId, Args, time.strftime("%a, %d %b %Y %H:%M:%S"))
        self.Operations.append(Op)

        if TableId not in self.Lineage:
            self.Lineage[TableId] = [OpId]
        else:
            self.Lineage[TableId] += [OpId]

    def __GetTableId(self):
        return 1 if len(self.Tables) == 0 else max(self.Tables) + 1
