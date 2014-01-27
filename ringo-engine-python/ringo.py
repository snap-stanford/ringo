import snap
import time
import inspect
import hashlib
import re

class RingoObject(object):
    def __init__(self, Id):
        self.Id = Id

    def __eq__(self, other):
        return self.Id == other.Id

    def __hash__(self):
        return hash(self.Id)

"""
Decorator used to automate the registration of TTable operations
"""
def registerOp(opName, trackOp = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            unpack_args = [arg.Id if isinstance(arg, RingoObject) else arg for arg in args]

            #If this is changed, GetHits must also be changed
            locals = inspect.getouterframes(inspect.currentframe())[1][0].f_locals
            ringo_locals = dict((var, locals[var]) for var in locals if isinstance(locals[var], RingoObject))
            for var in locals:
                if isinstance(locals[var], tuple):
                    all_ringo = True
                    for tuple_elem in locals[var]:
                        if not isinstance(tuple_elem, RingoObject):
                            all_ringo = False
                    if all_ringo == True: ringo_locals[var] = locals[var]
            args[0]._Ringo__UpdateNaming(ringo_locals)

            start_time = time.time()
            RetVal = func(*unpack_args, **kwargs)
            end_time = time.time()
            if trackOp:
                args[0]._Ringo__UpdateOperation(opName, RetVal, [args[1:], kwargs], end_time - start_time)
            return RetVal
        return wrapper
    return decorator

"""
Decorator used to track which parameters represent Column Names of which Tables
The column name metadata is a list of pairs of the form (c, t) where c is the index
    of the column name and t is the index of the corresponding table in the argument list
Populates FunctionTableCols
"""
#dictionary from function name to column name metadata
FunctionTableCols = {}
def registerColName(opName, colNameList):
    FunctionTableCols[opName] = colNameList
    def decorator(func):
        return func
    return decorator

class Ringo(object):
    NODE_ATTR_NAME = "__node_attr"
    EDGE_SRC_ATTR_NAME = "__edge_src_attr"
    EDGE_DST_ATTR_NAME = "__edge_dst_attr"

    dataTypes = ['int', 'float', 'string']
    def __init__(self):
        # mapping between object ids and snap objects
        self.Objects = {}
        # mapping between ringo objects and their user-given names
        self.ObjectNames = {}
        # an operation record has the form: <id (int), type (string), result table id, argument list (as used in python interface; ringo objects are used for table arguments), time stamp>
        self.Operations = [] 
        # mapping between a object (id) and the sequence of operation ids that led to it
        self.Lineage = {}
        # mapping between a object (id) and the list of object ids it depends on
        self.Dependencies = {}
        # mapping between object ids and their metadata (dict)
        self.Metadata = {}
        # mapping between a object (id) and the ids of the networks that originated from it
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
    # S = [('name','string'), ('age','int'), ('weight','float')]
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv')
    # MyTable = ringo.LoadTableTSV(S, 'table.tsv', [0,1]) if we want to load only columns 'name' and 'age'
    @registerOp('LoadTableTSV')
    def LoadTableTSV(self, Schema, InFnm, SeparatorChar = '\t', HasTitleLine = False):
        # prepare parameters to call TTable::LoadSS
        S = snap.Schema()  # How should this be written ?
        for Col in Schema:
            if Col[1] == 'int':
                S.Add(snap.TStrTAttrPr(Col[0], snap.atInt))  # tentative TTable interface syntax...
            elif Col[1] == 'float':
                S.Add(snap.TStrTAttrPr(Col[0], snap.atFlt))  # tentative TTable interface syntax...
            elif Col[1] == 'string':
                S.Add(snap.TStrTAttrPr(Col[0], snap.atStr))  # tentative TTable interface syntax...
            else:
                print "Illegal type %s for attribute %s" % (Col[1], Col[0])

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
        T = snap.TTable.Load(SIn, Context)

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

    @registerOp('TableFromHashMap')
    def TableFromHashMap(self, HashId, ColName1, ColName2, TableIsStrKeys = False):
        HashMap = self.Objects[HashId]
        TableId = self.__GetObjectId()
        T = snap.TTable.TableFromHashMap(str(TableId), HashMap, ColName1, ColName2, self.Context, snap.TBool(TableIsStrKeys))
        self.__UpdateObjects(T, self.Lineage[HashId], TableId)
        return RingoObject(TableId)

    @registerOp('ShowMetadata', False)
    def ShowMetadata(self, ObjectId):
        template = '{0: <35}{1}'
        print template.format('Name', self.ObjectNames[RingoObject(ObjectId)])
        for Label, Info in self.Metadata[ObjectId]:
            print template.format(Label, re.sub('<#(\d+)>',
                lambda m: self.__GetName(RingoObject(int(m.group(1)))), str(Info)))

    @registerOp('ShowDependencies', False)
    def ShowDependencies(self, ObjectId, HideMiddle = False):
        def Outputter(self, ObjectId, TabCount):
            print '  '*TabCount + self.__GetName(RingoObject(ObjectId))
            for Parent in self.Dependencies[ObjectId]:
                Outputter(self, Parent, TabCount+1)

        print 'Dependency Tree'
        if HideMiddle:
            Ancestors = set()
            Parents = set()
            Parents.add(ObjectId)
            while len(Parents) > 0:
                Curr = Parents.pop()
                if len(self.Dependencies[Curr]) == 0:
                    Ancestors.add(Curr)
                for Obj in self.Dependencies[Curr]:
                    Parents.add(Obj)
            print self.__GetName(RingoObject(ObjectId))
            for Obj in Ancestors:
                if Obj != ObjectId:
                    print '  '+self.__GetName(RingoObject(Obj))
        else:
            Outputter(self, ObjectId, 0)

    @registerOp('ShowProvenance', False)
    def ShowProvenance(self, ObjectId):
        print 'Provenance Script:'
        print '------------------'
        print self.__GetProvenance(ObjectId)

    @registerOp('GetSchema', False)
    def GetSchema(self, TableId):
    	T = self.Objects[TableId]
	Schema = T.GetSchema()
	S = []

	for Col in Schema:
		ColName = Col.Val1.CStr()
		ColType = Col.Val2
		S.append((ColName, ColType))

	return S
    
    @registerOp('GetRows', False)
    def Rows(self, TableId, MaxRows = None):
	T = self.Objects[TableId]
	S = T.GetSchema()
        Names = []
        Types = []

        for i, attr in enumerate(S):
            Names.append(attr.GetVal1())
            Types.append(attr.GetVal2())

        RI = T.BegRI()
        Cnt = 0

        while RI < T.EndRI() and (MaxRows is None or Cnt < MaxRows):
            Elements = []

            for c,t in zip(Names,Types):
                if t == snap.atInt:
                    Elements.append(str(RI.GetIntAttr(c)))
                elif t == snap.atFlt:
                    Elements.append(RI.GetFltAttr(c))
                elif t == snap.atStr:
                    Elements.append(RI.GetStrAttr(c))
                else:
                    raise NotImplementedError("Unsupported column type")

	    yield Elements
		
            RI.Next()
            Cnt += 1

    @registerOp('DumpTableContent', False)
    def DumpTableContent(self, TableId, MaxRows = None):
        T = self.Objects[TableId]
        ColSpace = 25
        S = T.GetSchema()
        Template = ""
        Line = ""
        Names = []
        Types = []

        for i, attr in enumerate(S):
            Template += "{%d: <%d}" % (i, ColSpace)
            Names.append(attr.GetVal1())
            Types.append(attr.GetVal2())
            Line += "-" * ColSpace

        print Template.format(*Names)
        print Line

	for row in self.Rows(TableId, MaxRows):
            print Template.format(*row)

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
    def Select(self, TableId, Predicate, InPlace = True, CompConstant = False): 
        Args = (TableId, Predicate, InPlace)

        if not InPlace:
            TableId = self.__CopyTable(TableId)
            
        # Parse predicate
        elements = Predicate.split()
        if (len(elements) != 3):
            raise NotImplementedError('Only predicates of the form "Attr1 <op> Attr2" are supported')

        T = self.Objects[TableId]
        OpString = elements[1]
        try:
            Op = {
              '=': snap.EQ,
              '!=': snap.NEQ,
              '<': snap.LT,
              '<=': snap.LTE,
              '>': snap.GT,
              '>=': snap.GTE,
              'in': snap.SUBSTR,
              'contains': snap.SUPERSTR
            }[OpString]
        except KeyError:
            raise NotImplementedError("Operator %s undefined" % OpString)

        Schema = T.GetSchema()
        ColType = None
        for Col in Schema:
            if Col.Val1 == elements[0]:
                ColType = Col.Val2
        if ColType is None:
            raise ValueError("No column with name %s found" % elements[0])
 
        if CompConstant:
            if  ColType == snap.atInt:
                T.SelectAtomicIntConst(elements[0], int(elements[2]), Op)
            elif ColType == snap.atFlt:
                T.SelectAtomicFltConst(elements[0], float(elements[2]), Op)
            elif ColType == snap.atStr:
                T.SelectAtomicStrConst(elements[0], str(elements[2]), Op)
        else:
            T.SelectAtomic(elements[0], elements[2], Op)
        return RingoObject(TableId)

    # USE CASE 8 OK
    @registerOp('Project')
    def Project(self, TableId, Columns, InPlace = True):
        PrepCols = snap.TStrV()
        for Col in Columns:
            PrepCols.Add(Col)

        if not InPlace:
            TableId = __CopyTable(TableId)

        T = self.Objects[TableId]
        T.ProjectInPlace(PrepCols)
        return RingoObject(TableId)

    # UNTESTED
    @registerOp('Join')
    @registerColName('Join', [(2, 0), (3, 1)])
    def Join(self, LeftTableId, RightTableId, LeftAttr, RightAttr):
        LeftT = self.Objects[LeftTableId]
        RightT = self.Objects[RightTableId]
        JoinT = LeftT.Join(LeftAttr, RightT, RightAttr)
        JoinTId = self.__UpdateObjects(JoinT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
        return RingoObject(JoinTId)

    @registerOp('Union')
    def Union(self, LeftTableId, RightTableId, TableName):
	LeftT = self.Objects[LeftTableId]
	RightT = self.Objects[RightTableId]
	UnionT = LeftT.Union(RightT, TableName)
	UnionTId = self.__UpdateObjects(UnionT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
	return RingoObject(UnionTId)

    @registerOp('UnionAll')
    def UnionAll(self, LeftTableId, RightTableId, TableName):
	LeftT = self.Objects[LeftTableId]
	RightT = self.Objects[RightTableId]
	UnionT = LeftT.UnionAll(RightT, TableName)
	UnionTId = self.__UpdateObjects(UnionT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
	return RingoObject(UnionTId)

    @registerOp('Rename')
    def Rename(self, TableId, Column, NewLabel):
	T = self.Objects[TableId]
	T.Rename(Column, NewLabel)
	return RingoObject(TableId)

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

    @registerOp('ColMax')
    def ColMax(self, TableId, Attr1, Attr2, ResultAttrName):
        T = self.Objects[TableId]
        T.ColMax(Attr1, Attr2, ResultAttrName)
        return RingoObject(TableId)

    @registerOp('ColMin')
    def ColMin(self, TableId, Attr1, Attr2, ResultAttrName):
        T = self.Objects[TableId]
        T.ColMin(Attr1, Attr2, ResultAttrName)
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

        G = T.ToGraph(snap.aaFirst)
        GraphId = self.__UpdateObjects(G, self.Lineage[TableId])
        return RingoObject(GraphId)

    @registerOp('GetHits')
    def GetHits(self, GraphId):
        G = self.Objects[GraphId]
        HT1 = snap.TIntFltH()
        HT2 = snap.TIntFltH()

        snap.GetHits(G, HT1, HT2)
        HT1Id = self.__UpdateObjects(HT1, self.Lineage[GraphId])
        HT2Id = self.__UpdateObjects(HT2, self.Lineage[GraphId])
        RetVal = (RingoObject(HT1Id), RingoObject(HT2Id))

        return RetVal

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
    def GenerateProvenance(self, ObjectId, OutFnm):
        with open(OutFnm, 'w') as file:
            file.write(self.__GetProvenance(ObjectId))

    def __GetProvenance(self, ObjectId):
        Preamble = ['import sys', 'import ringo', '']
        Lines = []
        Files = []

        SchemaMap = {} #dictionary from ringo objects to a dictionary from names to variable names
        for OpId in self.Lineage[ObjectId]:
            Op = self.Operations[OpId] 

            SpecialArg = -1
            if Op[1] == 'LoadTableTSV' or Op[1] == 'SaveTableTSV' or Op[1] == 'SaveTableBinary':
                SpecialArg = 1
            elif Op[1] == 'LoadTableBinary':
                SpecialArg = 0

            FuncArgs = []
            for Arg in Op[3][0]:
                if SpecialArg == 0:
                    FuncArgs.append('filename'+str(len(Files)))
                    Files.append(self.__GetName(Arg))
                else:
                    FuncArgs.append(self.__GetName(Arg))
                SpecialArg -= 1
            for Arg in Op[3][1]:
                FuncArgs.append(str(Arg)+'='+self.__GetName(Op[3][1][Arg]))

            RetName = self.__GetName(Op[2])

            if Op[1] == 'LoadTableTSV':
                Schema = Op[3][0][0]
                SchemaPreamble = []
                TableSchemaMap = {}
                for i in xrange(len(Schema)):
                    VariablePair = ('%s_ColName%d' % (RetName, i+1), '%s_ColType%d' % (RetName, i+1))
                    TableSchemaMap[self.__GetName(Schema[i][0])] = VariablePair[0]
                    TableSchemaMap[self.__GetName(Schema[i][1])] = VariablePair[1]
                    SchemaPreamble.append('(%s, %s)' % VariablePair)
                SchemaPreamble = '[%s]' % str.join(', ', SchemaPreamble)
                Preamble.append('%s = %s' % (SchemaPreamble, FuncArgs[0]))
                FuncArgs[0] = SchemaPreamble
                SchemaMap[RetName] = TableSchemaMap
            elif Op[1] in FunctionTableCols: 
                for ColInd, TableInd in FunctionTableCols[Op[1]]:
                    if FuncArgs[TableInd] in SchemaMap:
                        FuncArgs[ColInd] = SchemaMap[FuncArgs[TableInd]][FuncArgs[ColInd]]

            FuncCall = 'engine.%s(%s)' % (Op[1], str.join(', ', FuncArgs))
            if RetName != str(Op[2]):
                FuncCall = RetName+' = '+FuncCall

            Lines.append(FuncCall)

        FinalName = self.__GetName(RingoObject(ObjectId))
        Lines.append('return '+FinalName)
         
        Script = str.join('\n', Preamble) + '\n\ndef generate(engine,'
        for x in xrange(len(Files)):
            if x != 0: Script += ', '
            Script += 'filename'+str(x)
        Script += '):\n'

        for Line in Lines:
            Script += '    '+Line+'\n'

        Script += '\nengine = ringo.Ringo()\n'
        Script += 'files = [%s]\n' % str.join(', ', Files)
        Script += 'for i in xrange(min(len(files), len(sys.argv)-1)):\n'
        Script += '    files[i] = sys.argv[i+1]\n'
        Script += FinalName + ' = generate(engine, *files)\n'

        return Script

    def __GetName(self, Value):
        if isinstance(Value, basestring):
            return "'"+Value+"'"
        try:
            if Value in self.ObjectNames:
                return self.ObjectNames[Value]
            elif isinstance(Value, RingoObject):
                return '<#%d>' % Value.Id
        except:
            pass
        if isinstance(Value, tuple):
            Ret = '('
            for SubVal in Value:
                Ret += self.__GetName(SubVal)+', '
            Ret = Ret[:-2]+')'
        return str(Value)

    def __CopyTable(self, TableId):
        T = snap.TTable.New(self.Objects[TableId], str(TableId))
        CopyTableId = self.__UpdateObjects(T, self.Lineage[TableId])
        return CopyTableId

    def __UpdateObjects(self, Object, Lineage, Id = None):
        if Id is None:
		Id = self.__GetObjectId()

        self.Objects[Id] = Object 
        self.Lineage[Id] = sorted(list(set(Lineage)))
        return Id

    def __UpdateOperation(self, OpType, RetVal, Args, Time):
        OpId = self.__AddOperation(OpType, RetVal, Args, Time)
        
        ObjectIds = [Object.Id for Object in RetVal] if isinstance(RetVal, tuple) else [RetVal.Id]
        for ObjectId in ObjectIds:
            if ObjectId not in self.Lineage:
                self.Lineage[ObjectId] = [OpId]
            else:
                self.Lineage[ObjectId] += [OpId]

        self.__UpdateMetadata(OpId)

    def __UpdateMetadata(self, OpId):
        Op = self.Operations[OpId]
        Objects = Op[2]
        if not isinstance(Objects, tuple):
            Objects = [Objects]
        for Object in Objects:
            Metadata = [] 
            self.__AddTypeSpecificInfo(self.Objects[Object.Id], Metadata) 

            Datasets = set()
            FuncArgs = []
            Dependencies = set()
            for Arg in Op[3][0]:
                FuncArgs.append(self.__GetName(Arg))
                if isinstance(Arg, RingoObject):
                    Datasets.update(dict(self.Metadata[Arg.Id])['Datasets'].split(', '))
                    Dependencies.add(Arg.Id)
            for Arg in Op[3][1]:
                Obj = Op[3][1][Arg]
                FuncArgs.append(str(Arg)+'='+self.__GetName(Obj))
                if isinstance(Obj, RingoObject):
                    Datasets.update(dict(self.Metadata[Obj.Id])['Datasets'].split(', '))
                    Dependencies.add(Arg.Id)
            if Op[1] == 'LoadTableTSV':
                Datasets.add(Op[3][0][1])
            LastCommand = '%s = %s(%s)' % (self.__GetName(Op[2]), Op[1], str.join(', ', FuncArgs))
            if Object.Id in Dependencies: Dependencies.remove(Object.Id)

            Metadata.append(('Datasets', str.join(', ', Datasets)))
 
            if Object.Id in self.Metadata:
                OldMeta = dict(self.Metadata[Object.Id])
                Metadata.append(('Inputs', OldMeta['Inputs']))
                Metadata.append(('Operation', OldMeta['Operation']))
                Metadata.append(('Command', OldMeta['Command']))
                Metadata.append(('Last Modification', LastCommand))
                self.Dependencies[Object.Id] |= Dependencies
            else:
                Metadata.append(('Inputs', str.join(', ', FuncArgs)))
                Metadata.append(('Operation', Op[1]))
                Metadata.append(('Command', LastCommand))
                self.Dependencies[Object.Id] = Dependencies


            Metadata.append(('Last Edited', Op[4]))
            Metadata.append(('Last Operation Time', '%.1fs' % Op[5]))
            TotalTime = 0
            for PrevOpId in self.Lineage[Object.Id]:
                TotalTime += self.Operations[PrevOpId][5]
            Metadata.append(('Total Creation Time', '%.1fs' % TotalTime))

                   
            Provenance = self.__GetProvenance(Object.Id)
            Metadata.append(('Provenance Script', '%d lines, %d characters'
                % (len(str.splitlines(Provenance)), len(Provenance))))

            self.Metadata[Object.Id] = Metadata

    def __AddTypeSpecificInfo(self, Object, Metadata):
        if isinstance(Object, snap.PTable):
            Metadata.append(('Type', 'Table'))
            Metadata.append(('Number of Rows', Object.GetNumRows()))
            Schema = []
            for attr in Object.GetSchema():
                Schema.append(attr.GetVal1())
                if attr.GetVal2() == snap.atInt:
                    Schema[-1] += ' (int)'
                elif attr.GetVal2() == snap.atFlt:
                    Schema[-1] += ' (float)'
                elif attr.GetVal2() == snap.atStr:
                    Schema[-1] += ' (string)'
            Metadata.append(('Schema', Schema))
        elif isinstance(Object, snap.PNEANet):
            Metadata.append(('Type', 'Network'))
            Metadata.append(('Number of Nodes', Object.GetNodes()))
            Metadata.append(('Number of Edges', Object.GetEdges()))
        elif str(type(Object))[-3] == 'H':
            Metadata.append(('Type', 'HashMap'))
            Metadata.append(('Number of Elements', Object.Len()))

    def __AddOperation(self, OpType, RetVal, Args, Time):
        OpId = len(self.Operations)
        Op = (OpId, OpType, RetVal, Args, time.strftime("%a, %d %b %Y %H:%M:%S"), Time)
        self.Operations.append(Op)
        return OpId

    def __UpdateNaming(self, Locals):
        for Var in Locals:
            Object = Locals[Var]
            if Object not in self.ObjectNames:
                self.ObjectNames[Object] = Var
                if isinstance(Object, tuple):
                    for i in xrange(len(Object)):
                        self.ObjectNames[Object[i]] = '%s[%d]' %(Var, i)

    def __GetObjectId(self):
	    if len(self.Objects) == 0:
		    return 1

	    return max(self.Objects) + 1
