import snap
import time
import inspect

class RingoObject(object):
    def __init__(self, Id):
        self.Id = Id

"""
Decorator used to automate the registration of TTable operations
"""
def registerOp(opName, trackOp = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            unpack_args = [arg.Id if isinstance(arg, RingoObject) else arg for arg in args]

            locals = inspect.getouterframes(inspect.currentframe())[1][0].f_locals
            locals = dict((var, locals[var]) for var in locals if isinstance(locals[var], RingoObject))

            RetVal = func(*unpack_args, **kwargs)
            if trackOp:
                args[0]._Ringo__UpdateOperation(opName, RetVal, [args[1:], kwargs], locals)
            return RetVal
        return wrapper
    return decorator

class Ringo(object):
    NODE_ATTR_NAME = "__node_attr"
    EDGE_SRC_ATTR_NAME = "__edge_src_attr"
    EDGE_DST_ATTR_NAME = "__edge_dst_attr"

    dataTypes = ['int', 'float', 'string']
    def __init__(self):
        # mapping between object ids and snap objects
        self.Objects = {}
        # an operation record has the form: <id (int), type (string), result table id, argument list (as used in python interface; table ids are used for table arguments), time stamp>
        self.Operations = [] 
        # mapping between a table (id) and the sequence of operation ids that led to it
        self.Lineage = {}
        # mapping between a table (id) and the ids of the networks that originated from it
        self.TableToNetworks = {}
        self.Context = snap.TTableContext()

    def __getattr__(self, name):
        if name in dir(snap):
            def wrapper(*args, **kwargs):
                unpack_args = [self.Objects[arg.Id] if isinstance(arg, RingoObject) else arg for arg in args]
                return getattr(snap, name)(*unpack_args, **kwargs)
            return wrapper
        else:
            raise AttributeError
        
    # Use case:
    # S = {'name':'string', 'age':'int', 'weight':'float'}
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv')
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv', [0,1]) if we want to load only columns 'name' and 'age'
    @registerOp('LoadTableTSV')
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
        TableId = self.__GetObjectId()
        T = snap.TTable.LoadSS(str(TableId), S, InFnm, self.Context, SeparatorChar, snap.TBool(HasTitleLine))
        self.__UpdateObjects(T, [], TableId)
        return RingoObject(TableId)
        
    # USE CASE 2 OK
    @registerOp('SaveTableTSV')
    def SaveTableTSV(self, TableId, OutFnm):
        T = self.Objects[TableId]
        T.SaveSS(OutFnm)
        return RingoObject(TableId)
    
    # UNTESTED
    @registerOp('LoadTableBinary')
    def LoadTableBinary(self, InFnm):
        SIn = TSIn(InFnm)
        T = TTable.Load(SIn, Context)

        #T's internal name will not match TId - is this an issue?
        TableId = self.__UpdateObjects(T, [])
        return RingoObject(TableId)

    # UNTESTED
    @registerOp('SaveTableBinary')
    def SaveTableBinary(self, TableId, OutFnm):
        T = self.Objects[TableId]
        SOut = TSOut(OutFnm)
        T.Save(SOut)
        return RingoObject(TableId)

    # UNTESTED
    def GetHistory(self, TableId):
        return str(Lineage[TableId]) #should discuss exact format of this

    # UNTESTED
    @registerOp('AddLabel')
    def AddLabel(self, TableId, Attr, Label):
        T = self.Objects[TableId]
        T.AddLabel(Attr, Label)
        return RingoObject(TableId)

    # UNTESTED
    @registerOp('Unique')
    def Unique(self, TableId, GroupByAttr, InPlace = True):
        Args = (TableId, GroupByAttr, InPlace)
        if not InPlace:
            TableId = __CopyTable(TableId)
        
        T = self.Objects[TableId]
        T.Unique(GroupByAttr)
        return RingoObject(TableId)

    # UNTESTED
    @registerOp('Unique')
    def Unique(self, TableId, GroupByAttrs, Ordered, InPlace = True):
        Args = (TableId, GroupByAttr, NewTable)
        Attrs = TStrV()
        for Attr in GroupByAttr:
            Attrs.Add(Attr)

        if not InPlace:
            TableId = __CopyTable(TableId)

        T = self.Objects[TableId]
        T.Unique(Attrs, Ordered)
        return RingoObject(TableId)

    # USE CASE 2 OK
    @registerOp('Select')
    def Select(self, TableId, Predicate, InPlace = True): 
        Args = (TableId, Predicate, InPlace)
        if not InPlace:
            TableId = self.__CopyTable(TableId)
            
        # Parse predicate
        elements = Predicate.split()
        if (len(elements) != 3):
            raise NotImplementedError('Only predicates of the form "Attr1 <op> Attr2" are supported')

        T = self.Objects[TableId]
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
        return RingoObject(TableId)

    # UNTESTED
    @registerOp('Project')
    def Project(self, TableId, Columns, InPlace = True):
        Args = (TableId, Predicate, NewTable)
        PrepCols = TStrV()
        for Col in Columns:
            PrepCols.Add(Col)

        if NewTable:
            TableId = __CopyTable(TableId)

        T = self.Objects[TableId]
        T.ProjectInPlace(PrepCols)
        return RingoObject(TableId)

    # UNTESTED
    @registerOp('Join')
    def Join(self, LeftTableId, RightTableId, LeftAttr, RightAttr):
        LeftT = self.Objects[LeftTableId]
        RightT = self.Objects[RightTableId]
        JoinT = LeftT.Join(LeftAttr, RightT, RightAttr)
        JoinTId = self.__UpdateObjects(JoinT, Lineage[LeftTableId] + Lineage[RightTableId])
        return RingoObject(JoinTId)

    # USE CASE 1 OK
    @registerOp('SelfJoin')
    def SelfJoin(self, TableId, Attr):
        T = self.Objects[TableId]
        JoinT = T.SelfJoin(Attr)
        JoinTId = self.__UpdateObjects(JoinT, self.Lineage[TableId])
        return RingoObject(JoinTId)

    @registerOp('Order')
    def Order(self, TableId, Attrs, Asc = False):
        T = self.Objects[TableId]
        V = snap.TStrV()
        for attr in Attrs:
            V.Add(attr)
        T.Order(V, "", snap.TBool(False), snap.TBool(Asc))
        return RingoObject(TableId)

    # USE CASE 1 OK
    @registerOp('ToGraph')
    def ToGraph(self, TableId, SrcCol, DstCol):
        T = self.Objects[TableId]
        T.SetSrcCol(SrcCol)
        T.SetDstCol(DstCol)
        # TODO: How do we reset attributes when we build several graphs out of the same TTable?
        SrcV = snap.TStrV()
        DstV = snap.TStrV()
        SrcV.Add(SrcCol)
        DstV.Add(DstCol)
        T.AddSrcNodeAttr(SrcV)
        T.AddDstNodeAttr(DstV)

        G = T.ToGraph(snap.FIRST)
        GraphId = self.__UpdateObjects(G, self.Lineage[TableId])
        return RingoObject(GraphId)

    # UNTESTED
    def GetOpType(self, OpId):
        return Operations[OpId][1]

    # USE CASE 2 OK
    @registerOp('PageRank')
    def PageRank(self, GraphId, ResultAttrName = 'PageRank', AddToNetwork = False, C = 0.85, Eps = 1e-4, MaxIter = 100):
        if AddToNetwork:
            raise NotImplementedError()

        Graph = self.Objects[GraphId]
        HT = snap.TIntFltH()
        snap.GetPageRank(Graph, HT, C, Eps, MaxIter)
        TableId = self.__GetObjectId()
        # NOTE: The argument snap.atStr only works if NODE_ATTR_NAME is a String attribute of the graph.
        # Some logic is needed to determine the attribute type
        T = snap.TTable.GetFltNodePropertyTable(Graph, str(TableId), HT, self.NODE_ATTR_NAME, snap.atStr, ResultAttrName, self.Context)
        self.__UpdateObjects(T, self.Lineage[GraphId], TableId)
        return RingoObject(TableId)

    @registerOp('GenerateProvenance', False)
    def GenerateProvenance(self, TableId, OutFnm):
        def GetName(Value, Locals):
            if isinstance(Value, basestring):
                return "'"+Value+"'"
            for Name in Locals:
                if Locals[Name] == Value:
                    return Name
            return str(Value)

        Info = inspect.getouterframes(inspect.currentframe())[1][0].f_locals

        Lines = ['engine=ringo.Ringo()']
        NumFiles = 0
        for OpId in self.Lineage[TableId]:
            Op = self.Operations[OpId] 
            FuncCall = 'engine.'+Op[1]+'('

            SpecialArg = -1
            if Op[1] == 'LoadTableTSV' or Op[1] == 'SaveTableTSV' or Op[1] == 'SaveTableBinary':
                SpecialArg = 1
            elif Op[1] == 'LoadTableBinary':
                SpecialArg = 0

            for Arg in Op[3][0]:
                if SpecialArg == 0:
                    FuncCall += 'filename'+str(NumFiles)+','
                    NumFiles += 1
                else:
                    FuncCall += GetName(Arg, Op[4])+','
                SpecialArg -= 1
            for Arg in Op[3][1]:
                FuncCall += str(Arg)+'='+GetName(Op[3][1][Arg], Op[4])+','
            FuncCall = FuncCall[:-1]+')'

            FindName = Info['locals'] if OpId+1>=len(self.Operations) else self.Operations[OpId+1][4]
            Name = GetName(Op[2], FindName)
            if Name != str(Op[2]):
                FuncCall = Name+'='+FuncCall

            Lines.append(FuncCall)
        Lines.append('return '+GetName(Info['args'][1], Info['locals']))
         
        Script = 'import ringo\n\ndef generate('
        for x in xrange(NumFiles):
            if x != 0: Script += ','
            Script += 'filename'+str(x)
        Script += '):\n'

        for Line in Lines:
            Script += '    '+Line+'\n'

        with open(OutFnm, 'w') as file:
            file.write(Script)

    def __CopyTable(TableId):
        T = TTable.New(self.Objects[TableId], TId)
        CopyTableId = self.__UpdateObjects(T, Lineage[TableId])
        return CopyTableId

    def __UpdateObjects(self, Object, Lineage, Id = None):
        if Id is None:
          Id = self.__GetObjectId()
        self.Objects[Id] = Object 
        self.Lineage[Id] = sorted(Lineage)
        return Id

    def __UpdateOperation(self, OpType, RetVal, Args, Locals):
        ObjectId = RetVal.Id
        OpId = len(self.Operations)
        Op = (OpId, OpType, RetVal, Args, Locals, time.strftime("%a, %d %b %Y %H:%M:%S"))
        self.Operations.append(Op)

        if ObjectId not in self.Lineage:
            self.Lineage[ObjectId] = [OpId]
        else:
            self.Lineage[ObjectId] += [OpId]

    def __GetObjectId(self):
        return 1 if len(self.Objects) == 0 else max(self.Objects) + 1
