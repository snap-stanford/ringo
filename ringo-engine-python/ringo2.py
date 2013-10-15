from snap import *
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
        self.Context = TTableContext.New()
        
    # Use case:
    # S = {'name':'string', 'age':'int', 'weight':'float'}
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv')
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv', [0,1]) if we want to load only columns 'name' and 'age'
    def LoadTableTSV(self, Schema, InFnm, RelevantCols = [], SeparatorChar = '\t', HasTitleLine = True):
        # prepare parameters to call TTable::LoadSS
        S = Table.Schema()  # How should this be written ?
        for attr in Schema:
            if Schema[attr] == 'int':
                S.Add(TStrTypPr(attr, TTable.INT))  # tentative TTable interface syntax...
            else if Schema[attr] == 'float':
                S.Add(TStrTypPr(attr, TTable.FLT))  # tentative TTable interface syntax...
            else if Schema[attr] == 'string':
                S.Add(TStrTypPr(attr, TTable.STR))  # tentative TTable interface syntax...
            else:
                print "Illegal type %s for attribute %s" % (Schema[attr], attr)
        RC = TIntV()
        for c in RelevantCols: 
            RC.Add(c)
        TableId = max(self.Tables)+1

        # Load input and create new TTable object
        T = TTable.LoadSS(TableId, S, InFnm, Context, RC, SeparatorChar, HasTitleLine)
        __UpdateTables(TableId, T, [])
        
        Args = (Schema, InFnm, RelevantCols, SeparatorChar, HasTitleLine)
        __UpdateOperation('load tsv', TableId, Args)
        return TableId
        
    def SaveTableTSV(self, TableId, OutFnm):
        T = Tables[TableId]
        T.SaveSS(OutFnm)
        __UpdateOperation('save tsv', TableId, (TableId, OutFnm))
    
    def LoadTableBinary(self, InFnm):
        SIn = TSIn(InFnm)
        T = TTable.Load(SIn, Context)

        #T's internal name will not match TId - is this an issue?
        TableId = max(self.Tables)+1
        __UpdateTables(TableId, T, [])
        __UpdateOperation('load binary', TableId, (InFnm))
        return TableId

    def SaveTableBinary(self, TableId, OutFnm):
        T = Tables[TableId]
        SOut = TSOut(OutFnm)
        T.Save(SOut)
        __UpdateOperation('save binary', TableId, (TableId, OutFnm))

    def GetHistory(self, TableId):
        return str(Lineage[TableId]) #should discuss exact format of this

    def AddLabel(self, TableId, Attr, Label):
        T = Tables[TableId]
        T.AddLabel(Attr, Label)
        __UpdateOperation('add label', TableId, (TableId, Attr, Label))

    def Unique(self, TableId, GroupByAttr, NewTable = False):
        Args = (TableId, GroupByAttr, NewTable)
        if NewTable:
            TableId = __CopyTable(TableId)
        
        T = Tables[TableId]
        T.Unique(GroupByAttr)
        __UpdateOperation('unique', TableId, Args)

        return TableId

    def Unique(self, TableId, GroupByAttrs, Ordered, NewTable = False):
        Args = (TableId, GroupByAttr, NewTable)
        Attrs = TStrV()
        for Attr in GroupByAttr
            Attrs.Add(Attr)

        if NewTable:
            TableId = __CopyTable(TableId)

        T = Tables[TableId]
        T.Unique(Attrs, Ordered)
        OpId = __UpdateOperation('unique', TableId, Args)

        return TableId

    def Select(self, TableId, Predicate, NewTable = False): 
        Args = (TableId, Predicate, NewTable)
        if NewTable:
            TableId = __CopyTable(TableId)
            
        T = Tables[TableId]
        T.Select(Predicate)
        __UpdateOperation('select', TableId, Args)

        return TableId

    def Project(self, TableId, Columns, NewTable = False):
        Args = (TableId, Predicate, NewTable)
        PrepCols = TStrV()
        for Col in Columns
            PrepCols.Add(Col)

        if NewTable:
            TableId = __CopyTable(TableId)

        T = Tables[TableId]
        T.ProjectInPlace(PrepCols)
        __UpdateOperation('project', TableId, Args)

    def Join(self, LeftTableId, RightTableId, LeftAttr, RightAttr):
        LeftT = Tables[LeftTableId]
        RightT = Tables[RightTableId]
        JoinT = LeftT.Join(LeftAttr, RightT, RightAttr)

        JoinTableId = max(self.Tables)+1
        __UpdateTables(JoinTableId, JoinT, Lineage[LeftTableId] + Lineage[RightTableId])
        __UpdateOperation('join', JoinTableId, (LeftTableId, RightTableId, LeftAttr, RightAttr))
        return JoinTableId
    
    def Join(self, TableId, Attr)
        T = Tables[TableId]
        JoinT = T.SelfJoin(Attr)

        JoinTableId = max(self.Tables+1)
        __UpdateTables(JoinTableId, JoinT, Lineage[TableId])
        __UpdateOperation('join', JoinTableId, (TableId, Arr))

    def GetOpType(self, OpId):
        return Operations[OpId][1]

    def __CopyTable(TableId):
        TId = max(self.Tables)+1
        T = TTable.New(Tables[TableId], TId)
        __UpdateTables(TId, T, Lineage[TableId])
        return TId

    def __UpdateTables(TableId, Table, Lineage):
        self.Tables[TableId] = Table
        self.Lineage[TableId] = sorted(Lineage)

    def __UpdateOperation(OpType, TableId, Args):
        OpId = len(Operations)
        Op = (OpId, OpType, TableId, Args, strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
        self.Operations.append(Op)

        if TableId not in self.Lineage:
            self.Lineage[TableId] = [OpId]
        else:
            self.Lineage[TableId] += [OpId]
