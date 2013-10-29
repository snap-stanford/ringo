import snap
from time import gmtime, strftime

class ringo(object):
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
    def LoadTableTSV(self, Schema, InFnm, RelevantCols = [], SeparatorChar = '\t', HasTitleLine = False):
        # prepare parameters to call TTable::LoadSS
        S = snap.Schema() 
        for attr in Schema:
            if Schema[attr] == 'int':
                S.Add(snap.TStrTAttrPr(attr, snap.atInt))  # tentative TTable interface syntax...
            elif Schema[attr] == 'float':
                S.Add(snap.TStrTAttrPr(attr, snap.atFlt))  # tentative TTable interface syntax...
            elif Schema[attr] == 'string':
                S.Add(snap.TStrTAttrPr(attr, snap.atStr))  # tentative TTable interface syntax...
            else:
                print "Illegal type %s for attribute %s" % (Schema[attr], attr)
        RC = snap.TIntV()
        for c in RelevantCols: 
            RC.Add(c)
        TableId = max(self.Tables)+1 if self.Tables else 1

        # Load input and create new TTable object
        T = snap.TTable.LoadSS(str(TableId), S, InFnm, self.Context, RC, SeparatorChar, snap.TBool(HasTitleLine))
        self.__UpdateTables(TableId, T, [])
        
        Args = (Schema, InFnm, RelevantCols, SeparatorChar, HasTitleLine)
        self.__UpdateOperation('load tsv', TableId, Args)
        return TableId
        
    def SaveTableTSV(self, TableId, OutFnm):
        T = self.Tables[TableId]
        T.SaveSS(OutFnm)
        self.__UpdateOperation('save tsv', TableId, (TableId, OutFnm))
    
    def LoadTableBinary(self, InFnm):
        SIn = TSIn(InFnm)
        T = TTable.Load(SIn, Context)

        #T's internal name will not match TId - is this an issue?
        TableId = max(self.Tables)+1 if self.Tables else 1
        self.__UpdateTables(TableId, T, [])
        self.__UpdateOperation('load binary', TableId, (InFnm))
        return TableId

    def SaveTableBinary(self, TableId, OutFnm):
        T = self.Tables[TableId]
        SOut = TSOut(OutFnm)
        T.Save(SOut)
        self.__UpdateOperation('save binary', TableId, (TableId, OutFnm))

    def GetHistory(self, TableId):
        return str(self.Lineage[TableId]) #should discuss exact format of this

    def AddLabel(self, TableId, Attr, Label):
        T = self.Tables[TableId]
        T.AddLabel(Attr, Label)
        self.__UpdateOperation('add label', TableId, (TableId, Attr, Label))

    def Unique(self, TableId, GroupByAttr, NewTable = False):
        Args = (TableId, GroupByAttr, NewTable)
        if NewTable:
            TableId = self.__CopyTable(TableId)
        
        T = self.Tables[TableId]
        T.Unique(GroupByAttr)
        self.__UpdateOperation('unique', TableId, Args)

        return TableId

    def Unique(self, TableId, GroupByAttrs, Ordered, NewTable = False):
        Args = (TableId, GroupByAttr, NewTable)
        Attrs = TStrV()
        for Attr in GroupByAttr:
            Attrs.Add(Attr)

        if NewTable:
            TableId = self.__CopyTable(TableId)

        T = self.Tables[TableId]
        T.Unique(Attrs, Ordered)
        OpId = self.__UpdateOperation('unique', TableId, Args)

        return TableId

    def Select(self, TableId, Predicate, NewTable = False): 
        Args = (TableId, Predicate, NewTable)
        if NewTable:
            TableId = self.__CopyTable(TableId)
            
        T = self.Tables[TableId]
        T.Select(Predicate)
        self.__UpdateOperation('select', TableId, Args)

        return TableId

    def Project(self, TableId, Columns, NewTable = False):
        Args = (TableId, Predicate, NewTable)
        PrepCols = TStrV()
        for Col in Columns:
            PrepCols.Add(Col)

        if NewTable:
            TableId = self.__CopyTable(TableId)

        T = self.Tables[TableId]
        T.ProjectInPlace(PrepCols)
        self.__UpdateOperation('project', TableId, Args)

    def Join(self, LeftTableId, RightTableId, LeftAttr, RightAttr):
        LeftT = self.Tables[LeftTableId]
        RightT = self.Tables[RightTableId]
        JoinT = LeftT.Join(LeftAttr, RightT, RightAttr)

        JoinTableId = max(self.Tables)+1
        self.__UpdateTables(JoinTableId, JoinT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
        self.__UpdateOperation('join', JoinTableId, (LeftTableId, RightTableId, LeftAttr, RightAttr))
        return JoinTableId
    
    def Join(self, TableId, Attr):
        T = self.Tables[TableId]
        JoinT = T.SelfJoin(Attr)

        JoinTableId = max(self.Tables)+1
        self.__UpdateTables(JoinTableId, JoinT, self.Lineage[TableId])
        self.__UpdateOperation('join', JoinTableId, (TableId, Attr))
        return JoinTableId

    def Graph(self, TableId, SrcCol, DstCol):
        T = self.Tables[TableId]
        T.SetSrcCol(SrcCol)
        T.SetDstCol(DstCol)
        return T.ToGraph(snap.MIN)

    def GetOpType(self, OpId):
        return self.Operations[OpId][1]

    def __CopyTable(self, TableId):
        TId = max(self.Tables)+1
        T = TTable.New(self.Tables[TableId], TId)
        self.__UpdateTables(TId, T, self.Lineage[TableId])
        return TId

    def __UpdateTables(self, TableId, Table, Lineage):
        self.Tables[TableId] = Table
        self.Lineage[TableId] = sorted(Lineage)

    def __UpdateOperation(self, OpType, TableId, Args):
        OpId = len(self.Operations)
        strftime("%a, %d %b %Y %H:%M:%S", gmtime())
        Op = (OpId, OpType, TableId, Args, strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
        self.Operations.append(Op)

        if TableId not in self.Lineage:
            self.Lineage[TableId] = [OpId]
        else:
            self.Lineage[TableId] += [OpId]
