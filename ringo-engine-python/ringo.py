import snap
import time
import inspect
import hashlib
import re
import socket
import json
import types

def inspectStack(ringo, stackFrameOffset):
    locals = inspect.getouterframes(inspect.currentframe())[1+stackFrameOffset][0].f_locals
    ringo_locals = dict((var, locals[var]) for var in locals if isinstance(locals[var], RingoObject))
    for var in locals:
        if isinstance(locals[var], tuple):
            all_ringo = True
            for tuple_elem in locals[var]:
                if not isinstance(tuple_elem, RingoObject):
                    all_ringo = False
            if all_ringo == True: ringo_locals[var] = locals[var]

    ringo._Ringo__UpdateNaming(ringo_locals)

"""
Decorator used to automate the registration of TTable operations
"""
def registerOp(opName, trackOp = True, stackFrameOffset = 0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ringo = args[0]
            if isinstance(ringo, RingoObject):
                ringo = ringo.Ringo
            inspectStack(ringo, stackFrameOffset+1)

            unpack_args = [arg.Id if isinstance(arg, RingoObject) else arg for arg in args]

            start_time = time.time()
            RetVal = func(*unpack_args, **kwargs)
            end_time = time.time()
            if trackOp:
                ringo._Ringo__UpdateOperation(opName, RetVal, [args[1:], kwargs], end_time - start_time, args[0])
            return RetVal
        return wrapper
    return decorator

class RingoObject(object):
    def __init__(self, Id, Ringo):
        self.Id = Id
        self.Ringo = Ringo

    def __eq__(self, other):
        return self.Id == other.Id

    def __hash__(self):
        return hash(self.Id)

    def __iter__(self):
        Obj = self.__GetSnapObj()
        return Obj.__iter__()

    def __contains__(self, elem):
        Obj = self.__GetSnapObj()
        return Obj.__contains__(elem)

    @registerOp('__getitem__', stackFrameOffset=1)
    def __getitem__(self, key):
        Obj = self.__GetSnapObj()
        return Obj.__getitem__(key)

    @registerOp('__setitem__', stackFrameOffset=1)
    def __setitem__(self, key, item):
        Obj = self.__GetSnapObj()
        Obj.__setitem__(key, item)

    def __len__(self):
        Obj = self.__GetSnapObj()
        return len(Obj)

    def __getattr__(self, name):
        Obj = self.__GetSnapObj()
        if hasattr(self.Ringo, name):
            inspectStack(self.Ringo, 1)
            def wrapper(*args, **kwargs):
                return getattr(self.Ringo, name)(self, *args, **kwargs)
            return wrapper
        if hasattr(Obj, name):
            def wrapper(*args, **kwargs):
                def func(self, *args, **kwargs):
                    Ret = getattr(Obj, name)(*args, **kwargs)

                return registerOp(name, stackFrameOffset=1)(func)(self, *args, **kwargs)
            return wrapper
        raise AttributeError

    def __GetSnapObj(self):
        return self.Ringo.Objects[self.Id]

# A utility function to determine if two names are an alias for the same table attribute        
def colNamesEqual(name1, name2):
	return snap.TTable.NormalizeColName(name1) == snap.TTable.NormalizeColName(name2) 

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
        # mapping between an id and a record
        # an operation record has the form: <id (string), type (string), result id, argument list (as used in python interface; ringo objects are used for table arguments), time stamp, object on which operation was called>
        self.Operations = {} 
        # mapping between a object (id) and the sequence of operation ids that led to it
        self.Lineage = {}
        # mapping between a object (id) and the list of object ids it depends on
        self.Dependencies = {}
        # mapping between object ids and their metadata (dict)
        self.Metadata = {}

        self.Context = snap.TTableContext()

    def __getattr__(self, name):
        match = re.match('Construct(\w*)', name)
        if match is not None and match.group(1) in dir(snap):
            ObjName = match.group(1)
            def func(self, *args, **kwargs):
                Obj = getattr(snap, ObjName)(*args, **kwargs)
                Id = self.__UpdateObjects(Obj, [])
                return RingoObject(Id, self)
            def wrapper(*args, **kwargs):
                return registerOp(name)(func)(self, *args, **kwargs)
            return wrapper

        if hasattr(snap, name) and type(getattr(snap,name)) == types.TypeType:
            Obj = getattr(snap, name)
            Id = self.__UpdateObjects(Obj, [])
            Ret = RingoObject(Id, self)
            self.__UpdateNaming({self.__GetName(self) + '.' + name: Ret})
            return RingoObject(Id, self)
            
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
        TableId = self.__GetId(self.Objects)
        T = snap.TTable.LoadSS(S, InFnm, self.Context, SeparatorChar, snap.TBool(HasTitleLine))
        self.__UpdateObjects(T, [], TableId)
        return RingoObject(TableId, self)
        
    # USE CASE 2 OK
    @registerOp('SaveTableTSV')
    def SaveTableTSV(self, TableId, OutFnm):
        T = self.Objects[TableId]
        T.SaveSS(OutFnm)
        return RingoObject(TableId, self)
    
    @registerOp('Load', False)
    def Load(self, InFnm):
        def ConvertJSON(JSON):
            if isinstance(JSON, dict):
                return dict([(ConvertJSON(key), ConvertJSON(JSON[key])) for key in JSON])
            elif isinstance(JSON, list):
                return [ConvertJSON(value) for value in JSON]
            elif isinstance(JSON, unicode):
                return JSON.encode('UTF-8')
            else:
                return JSON
        def UnpackObject(self, Packed):
            ObjectId = Packed['Id']
            self.ObjectNames[RingoObject(ObjectId, self)] = Packed['Name']
            self.Lineage[ObjectId] = Packed['Lineage']
            self.Dependencies[ObjectId] = Packed['Dependencies']
            self.Metadata[ObjectId] = Packed['Metadata']
        def ObjectDecoder(Object):
            if 'RingoObject' in Object:
                return RingoObject(Object['Id'], self)
            elif 'Set' in Object:
                return set(Object['Content'])
            elif 'Ringo' in Object:
                return self
            else:
                return Object

        with open(InFnm+'.json') as inp:
            JSON = ConvertJSON(json.load(inp, object_hook = ObjectDecoder))

        for OpId in JSON['Operations']:
            self.Operations[OpId] = JSON['Operations'][OpId]

        for ObjectId in JSON['Objects']:
            UnpackObject(self, JSON['Objects'][ObjectId])

        SIn = snap.TFIn(InFnm+'.bin')
        if JSON['Type'] == 'TTable':
            Obj = getattr(snap, JSON['Type']).Load(SIn, self.Context)
        else:
            Obj = getattr(snap, JSON['Type']).Load(SIn)
        ObjId = JSON['ID']
        self.__UpdateObjects(Obj, self.Lineage[ObjId], ObjId)
        return RingoObject(ObjId, self)

    # UNTESTED
    @registerOp('Save', False)
    def Save(self, ObjectId, OutFnm):
        def PackObject(self, ObjectId):
            Pack = {}
            Pack['Id'] = ObjectId
            Pack['Name'] = self.ObjectNames[RingoObject(ObjectId, self)]
            Pack['Lineage'] = self.Lineage[ObjectId]
            Pack['Dependencies'] = self.Dependencies[ObjectId]
            Pack['Metadata'] = self.Metadata[ObjectId]
            return Pack
        def AssembleObject(self, ObjectId):
            Assembled = {ObjectId: PackObject(self,ObjectId)}
            for Parent in self.Dependencies[ObjectId]:
                Assembled.update(AssembleObject(self, Parent))
            return Assembled
        def ObjectEncoder(Object):
            if isinstance(Object, RingoObject):
                return {'RingoObject':True, 'Id':Object.Id}
            elif isinstance(Object, dict):
                return Object
            elif isinstance(Object, set):
                return {'Set':True, 'Content':list(Object)}
            elif isinstance(Object, Ringo):
                return {'Ringo':True}
            raise TypeError(type(Object))

        Object = self.Objects[ObjectId]

        JSON = {}
        JSON['Operations'] = dict([(Id, self.Operations[Id]) for Id in self.Lineage[ObjectId]])
        JSON['Objects'] = AssembleObject(self, ObjectId)
        JSON['ID'] = ObjectId

        TypeMatch = re.match("<class 'snap.(\w*)'>", str(type(Object)))
        if TypeMatch is None:
            raise TypeError('Given object is not a snap object')
        Type = TypeMatch.group(1)
        if Type[0] == 'P':
            Type = 'T' + Type[1:]
        JSON['Type'] = Type

        with open(OutFnm+'.json', 'w') as out:
            json.dump(JSON, out, default = ObjectEncoder)

        SOut = snap.TFOut(OutFnm+'.bin')
        Object.Save(SOut)

    @registerOp('TableFromHashMap')
    def TableFromHashMap(self, HashId, ColName1, ColName2, TableIsStrKeys = False):
        HashMap = self.Objects[HashId]
        TableId = self.__GetId(self.Objects)
        T = snap.TTable.TableFromHashMap(HashMap, ColName1, ColName2, self.Context, snap.TBool(TableIsStrKeys))
        self.__UpdateObjects(T, self.Lineage[HashId], TableId)
        return RingoObject(TableId, self)

    @registerOp('ShowMetadata', False)
    def ShowMetadata(self, ObjectId):
        template = '{0: <35}{1}'
        print template.format('Name', self.ObjectNames[RingoObject(ObjectId, self)])
        for Label, Info in self.Metadata[ObjectId]:
            print template.format(Label, re.sub('<#(\d+)>',
                lambda m: self.__GetName(RingoObject(int(m.group(1)))), str(Info)))

    @registerOp('ShowDependencies', False)
    def ShowDependencies(self, ObjectId, HideMiddle = False):
        def Outputter(self, ObjectId, TabCount):
            print '  '*TabCount + self.__GetName(RingoObject(ObjectId, self))
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
            print self.__GetName(RingoObject(ObjectId, self))
            for Obj in Ancestors:
                if Obj != ObjectId:
                    print '  '+self.__GetName(RingoObject(Obj, self))
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
        return RingoObject(TableId, self)

    # UNTESTED
    @registerOp('Unique')
    def Unique(self, TableId, GroupByAttr, InPlace = True):
        if not InPlace:
            TableId = self.__CopyTable(TableId)
        
        T = self.Objects[TableId]
        T.Unique(GroupByAttr)
        return RingoObject(TableId, self)

    # UNTESTED
    @registerOp('Unique')
    def Unique(self, TableId, GroupByAttrs, Ordered, InPlace = True):
        Attrs = TStrV()
        for Attr in GroupByAttr:
            Attrs.Add(Attr)

        if not InPlace:
            TableId = self.__CopyTable(TableId)

        T = self.Objects[TableId]
        T.Unique(Attrs, Ordered)
        return RingoObject(TableId, self)

    # USE CASE 2 OK
    @registerOp('Select')
    def Select(self, TableId, Predicate, InPlace = True): 
        def GetOp(OpString):
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
            return Op
        def GetColType(Schema, ColName):
            for Col in Schema:
                if colNamesEqual(Col.Val1.CStr(), ColName):
                    return Col.Val2
            raise ValueError("No column with name %s found" % ColName)
        def IsConstant(Arg):
            if '0' <= Arg[0] and Arg[0] <= '9':
                return True
            return Arg[0] == "'" or Arg[0] == '"'
        def Merge(Expression):
            while '(' in Expression:
                left = Expression.index('(')
                right = left+1
                count = 0
                while count > 0 or Expression[right] != ')':
                    if Expression[right] == ')':
                        count += 1
                    elif Expression[right] == '(':
                        count -= 1
                    right += 1
                Expression[left:right+1] = Merge(Expression[left+1:right])

            while 'and' in Expression:
                op = Expression.index('and')
                Merged = snap.TPredicateNode(snap.AND)
                Merged.addLeftChild(Expression[op-1])
                Merged.addRightChild(Expression[op+1])
                Expression[op-1:op+2] = snap.TPredicate(Merged)

            while 'or' in Expression:
                op = Expression.index('or')
                Merged = snap.TPredicateNode(snap.OR)
                Merged.addLeftChild(Expression[op-1])
                Merged.addRightChild(Expression[op+1])
                Expression[op-1:op+2] = snap.TPredicate(Merged)

            if len(Expression) > 1:
                raise ValueError("Invalid expression - too many operands") 
            return Expression[0]
        def ConstructPredicate(elements, Schema):
            Expression = []
            i = 0
            NumParens = 0
            while i < len(elements):
                if i > 0:
                    if elements[i].lower() == 'and':
                        Expression.append('and')
                    elif elements[i].lower() == 'or':
                        Expression.append('or')
                    else:
                        raise ValueError("Improper conjuction %s: only AND/OR supported" % elements[i])
                    i += 1

                while elements[i] == '(':
                    Expression.append('(')
                    NumParens += 1
                    i += 1
    
                Left = elements[i]
                ColType = GetColType(Schema, Left)
                Op = GetOp(elements[i+1])
                Right = elements[i+2]
                if IsConstant(Right):
                    Args = ()
                    if ColType == snap.atInt:
                        Args = (int(Right), 0, "")
                    elif ColType == snap.atFlt:
                        Args = (0, float(Right), "")
                    elif ColType == snap.atStr:
                        Args = (0, 0, Right[1:-1])
                    Expression.append(snap.TAtomicPredicate(ColType, snap.TBool(True), Op, Left, "",
                        *Args))
                else:
                    Expression.append(snap.TAtomicPredicate(ColType, snap.TBool(False), Op, Left, Right))

                i += 2
                while element[i] == ')':
                    Expression.append(')')
                    NumParens -= 1
                    i += 1
                if NumParens < 0:
                    raise ValueError("Unbalanced parentheses found")
                
            if NumParens !=0:
                raise ValueError("Unbalanced parentheses found")
            return Merge(Expression)

        if not InPlace:
            TableId = self.__CopyTable(TableId)
            
        # Parse predicate
        elements = Predicate.split()

        special = ['\(', '\)', '=', '!', '<', '>']
        pat = '((?:%s)*)' % '|'.join(special)
        elements = [j for i in map(lambda s: re.split(pat, s), elements) for j in i if len(j) > 0]

        T = self.Objects[TableId]
        Schema = T.GetSchema()
        
        if (len(elements) == 3):
            Op = GetOp(elements[1])
    
            ColType = GetColType(Schema, elements[0])     

            if IsConstant(elements[2]):
                if  ColType == snap.atInt:
                    T.SelectAtomicIntConst(elements[0], int(elements[2]), Op)
                elif ColType == snap.atFlt:
                    T.SelectAtomicFltConst(elements[0], float(elements[2]), Op)
                elif ColType == snap.atStr:
                    T.SelectAtomicStrConst(elements[0], str(elements[2][1:-1]), Op)
            else:
                T.SelectAtomic(elements[0], elements[2], Op)
        else:
            T.Select(ConstructPredicate(elements, Schema))
        return RingoObject(TableId, self)

    # USE CASE 8 OK
    @registerOp('Project')
    def Project(self, TableId, Columns, InPlace = True):
        PrepCols = snap.TStrV()
        for Col in Columns:
            PrepCols.Add(Col)

        if not InPlace:
            TableId = self.__CopyTable(TableId)

        T = self.Objects[TableId]
        T.ProjectInPlace(PrepCols)
        return RingoObject(TableId, self)

    # UNTESTED
    @registerOp('Join')
    def Join(self, LeftTableId, RightTableId, LeftAttr, RightAttr):
        LeftT = self.Objects[LeftTableId]
        RightT = self.Objects[RightTableId]
        JoinT = LeftT.Join(LeftAttr, RightT, RightAttr)
        JoinTId = self.__UpdateObjects(JoinT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
        return RingoObject(JoinTId, self)

    @registerOp('Union')
    def Union(self, LeftTableId, RightTableId):
        LeftT = self.Objects[LeftTableId]
        RightT = self.Objects[RightTableId]
        UnionT = LeftT.Union(RightT)
        UnionTId = self.__UpdateObjects(UnionT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
        return RingoObject(UnionTId, self)

    @registerOp('UnionAll')
    def UnionAll(self, LeftTableId, RightTableId):
        LeftT = self.Objects[LeftTableId]
        RightT = self.Objects[RightTableId]
        UnionT = LeftT.UnionAll(RightT)
        UnionTId = self.__UpdateObjects(UnionT, self.Lineage[LeftTableId] + self.Lineage[RightTableId])
        return RingoObject(UnionTId, self)

    @registerOp('Rename')
    def Rename(self, TableId, Column, NewLabel):
        T = self.Objects[TableId]
        T.Rename(Column, NewLabel)
        return RingoObject(TableId, self)

    # USE CASE 1 OK
    @registerOp('SelfJoin')
    def SelfJoin(self, TableId, Attr):
        T = self.Objects[TableId]
        JoinT = T.SelfJoin(Attr)
        JoinTId = self.__UpdateObjects(JoinT, self.Lineage[TableId])
        return RingoObject(JoinTId, self)

    @registerOp('Order')
    def Order(self, TableId, Attrs, Asc = False, InPlace = True):
        if not InPlace:
            TableId = self.__CopyTable(TableId)

        T = self.Objects[TableId]
        V = snap.TStrV()
        for attr in Attrs:
            V.Add(attr)
        T.Order(V, "", snap.TBool(False), snap.TBool(Asc))
        return RingoObject(TableId, self)

    @registerOp('ColMax')
    def ColMax(self, TableId, Attr1, Attr2, ResultAttrName):
        T = self.Objects[TableId]
        T.ColMax(Attr1, Attr2, ResultAttrName)
        return RingoObject(TableId, self)

    @registerOp('ColMin')
    def ColMin(self, TableId, Attr1, Attr2, ResultAttrName):
        T = self.Objects[TableId]
        T.ColMin(Attr1, Attr2, ResultAttrName)
        return RingoObject(TableId, self)

    # USE CASE 1 OK
    @registerOp('ToGraph')
    def ToGraph(self, TableId, SrcCol, DstCol, Directed = True):
        T = self.Objects[TableId]
        
        G = snap.ToGraph(snap.PNGraph if Directed else snap.PUNGraph, T, SrcCol, DstCol, snap.aaFirst)
        GraphId = self.__UpdateObjects(G, self.Lineage[TableId])
        return RingoObject(GraphId, self)

    @registerOp('GetHits')
    def GetHits(self, GraphId):
        G = self.Objects[GraphId]
        HT1 = snap.TIntFltH()
        HT2 = snap.TIntFltH()

        snap.GetHits(G, HT1, HT2)
        HT1Id = self.__UpdateObjects(HT1, self.Lineage[GraphId])
        HT2Id = self.__UpdateObjects(HT2, self.Lineage[GraphId])
        RetVal = (RingoObject(HT1Id, self), RingoObject(HT2Id, self))

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
        # Which version of PageRank is called ?
        snap.GetPageRank(Graph, HT, C, Eps, MaxIter)
        TableId = self.__GetId(self.Objects)
        HTId = self.__UpdateObjects(HT, self.Lineage[GraphId])
        return RingoObject(HTId, self)

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

            Callee = Op[6]
            if isinstance(Callee, RingoObject):
                Callee = self.__GetName(Callee)
            else:
                Callee = self.__GetName(self)
            FuncCall = '%s.%s(%s)' % (Callee, Op[1], str.join(', ', FuncArgs))
            if RetName != str(Op[2]):
                FuncCall = RetName+' = '+FuncCall

            Lines.append(FuncCall)

        FinalName = self.__GetName(RingoObject(ObjectId, self))
        Lines.append('return '+FinalName)
         
        Script = str.join('\n', Preamble) + '\n\ndef generate(' + self.__GetName(self)
        for x in xrange(len(Files)):
            Script += ', filename'+str(x)
        Script += '):\n'

        for Line in Lines:
            Script += '    '+Line+'\n'

        Script += '\n%s = ringo.Ringo()\n' % self.__GetName(self)
        Script += 'files = [%s]\n' % str.join(', ', Files)
        Script += 'for i in xrange(min(len(files), len(sys.argv)-1)):\n'
        Script += '    files[i] = sys.argv[i+1]\n'
        Script += FinalName + ' = generate(%s, *files)\n' % self.__GetName(self)

        return Script

    def __GetName(self, Value):
        if isinstance(Value, basestring):
            return "'"+Value+"'"
        if isinstance(Value, Ringo):
            return "engine"
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
                SubName = self.__GetName(SubVal)
                if SubName == str(SubVal):
                    SubName = '_'
                Ret += SubName+', '
            Ret = Ret[:-2]+')'
        return str(Value)

    def __CopyTable(self, TableId):
        T = snap.TTable.New(self.Objects[TableId])
        CopyTableId = self.__UpdateObjects(T, self.Lineage[TableId])
        return CopyTableId

    def __UpdateObjects(self, Object, Lineage, Id = None):
        if Id is None:
            Id = self.__GetId(self.Objects)

        self.Objects[Id] = Object 
        self.Lineage[Id] = sorted(list(set(Lineage)))
        return Id

    def __UpdateOperation(self, OpType, RetVal, Args, Time, Callee):
        OpId = self.__AddOperation(OpType, RetVal, Args, Time, Callee)
        
        if not isinstance(RetVal, tuple):
            RetVal = [RetVal]
        ObjectIds = [Object.Id for Object in RetVal if isinstance(Object, RingoObject)]
        if isinstance(Callee, RingoObject):
            ObjectIds.append(Callee.Id)

        for ObjectId in ObjectIds:
            if ObjectId not in self.Lineage:
                self.Lineage[ObjectId] = [OpId]
            else:
                self.Lineage[ObjectId] += [OpId]

        self.__UpdateMetadata(OpId)

    def __UpdateMetadata(self, OpId):
        Op = self.Operations[OpId]
        Objects = Op[2]
        Objects = [Obj for Obj in Objects] if isinstance(Objects, tuple) else [Objects]
        Objects.append(Op[5])

        for Object in Objects:
            if not isinstance(Object, RingoObject):
                continue
            Metadata = [] 
            self.__AddTypeSpecificInfo(self.Objects[Object.Id], Metadata) 

            Datasets = set()
            FuncArgs = []
            Dependencies = set()
            for Arg in Op[3][0]:
                FuncArgs.append(self.__GetName(Arg))
                if isinstance(Arg, RingoObject) and Arg.Id in self.Metadata:
                    Datasets.update(dict(self.Metadata[Arg.Id])['Datasets'].split(', '))
                    Dependencies.add(Arg.Id)
            for Arg in Op[3][1]:
                Obj = Op[3][1][Arg]
                FuncArgs.append(str(Arg)+'='+self.__GetName(Obj))
                if isinstance(Obj, RingoObject) and Obj.Id in self.Metadata:
                    Datasets.update(dict(self.Metadata[Obj.Id])['Datasets'].split(', '))
                    Dependencies.add(Arg.Id)
            if Op[1] == 'LoadTableTSV':
                Datasets.add(Op[3][0][1])
            
            MethodCall = Op[1]
            if isinstance(Op[6], RingoObject):
                MethodCall = self.__GetName(Op[6]) + MethodCall
            LastCommand = '%s = %s(%s)' % (self.__GetName(Op[2]), MethodCall, str.join(', ', FuncArgs))
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

    def __AddOperation(self, OpType, RetVal, Args, Time, Callee):
        OpId = self.__GetId(self.Operations)
        Op = (OpId, OpType, RetVal, Args, time.strftime("%a, %d %b %Y %H:%M:%S"), Time, Callee)
        self.Operations[OpId] = Op
        return OpId

    def __UpdateNaming(self, Locals):
        for Var in Locals:
            Object = Locals[Var]
            if Object not in self.ObjectNames:
                self.ObjectNames[Object] = Var
                if isinstance(Object, tuple):
                    for i in xrange(len(Object)):
                        self.ObjectNames[Object[i]] = '%s[%d]' %(Var, i)

    def __GetId(self, Container):
        Prefix = socket.gethostname()+'_'+time.strftime("%Y%m%d_%H%M%S")
        Num = 0
        while True:
            Id = Prefix+'_'+str(Num)
            if Id not in Container:
                break
            Num += 1
        return Id

    @registerOp('CntInDegNodes', False)
    def CntInDegNodes(self, GraphId, NodeInDeg):
        Graph = self.Objects[GraphId]
        Count = snap.CntInDegNodes(Graph, NodeInDeg)
        return Count

    @registerOp('CntOutDegNodes', False)
    def CntOutDegNodes(self, GraphId, NodeOutDeg):
        Graph = self.Objects[GraphId]
        Count = snap.CntOutDegNodes(Graph, NodeOutDeg)
        return Count

    @registerOp('CntDegNodes', False)
    def CntDegNodes(self, GraphId, NodeDeg):
        Graph = self.Objects[GraphId]
        Count = snap.CntDegNodes(Graph, NodeDeg)
        return Count

    @registerOp('CntNonZNodes', False)
    def CntNonZNodes(self, GraphId):
        Graph = self.Objects[GraphId]
        Count = snap.CntNonZNodes(Graph)
        return Count

    @registerOp('CntEdgesToSet', False)
    def CntEdgesToSet(self, GraphId, NId, NodeSetId):
        Graph = self.Objects[GraphId]
        NodeSet = self.Objects[NodeSetId]
        Count = snap.CntEdgesToSet(Graph, NId, NodeSet)
        return Count

    @registerOp('GetMxDegNId', False)
    def GetMxDegNId(self, GraphId):
        Graph = self.Objects[GraphId]
        NId = snap.GetMxDegNId(Graph)
        return NId

    @registerOp('GetMxInDegNId', False)
    def GetMxInDegNId(self, GraphId):
        Graph = self.Objects[GraphId]
        NId = snap.GetMxInDegNId(Graph)
        return NId

    @registerOp('GetMxOutDegNId', False)
    def GetMxOutDegNId(self, GraphId):
        Graph = self.Objects[GraphId]
        NId = snap.GetMxOutDegNId(Graph)
        return NId

    @registerOp('GetInDegCnt')
    def GetInDegCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        DegToCntV = snap.TIntPrV()
        snap.GetInDegCnt(Graph, DegToCntV)
        DegToCntVId = self.__UpdateObjects(DegToCntV, self.Lineage[GraphId])
        return RingoObject(DegToCntVId, self)

    @registerOp('GetOutDegCnt')
    def GetOutDegCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        DegToCntV = snap.TIntPrV()
        snap.GetOutDegCnt(Graph, DegToCntV)
        DegToCntVId = self.__UpdateObjects(DegToCntV, self.Lineage[GraphId])
        return RingoObject(DegToCntVId, self)

    @registerOp('GetDegCnt')
    def GetDegCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        DegToCntV = snap.TIntPrV()
        snap.GetDegCnt(Graph, DegToCntV)
        DegToCntVId = self.__UpdateObjects(DegToCntV, self.Lineage[GraphId])
        return RingoObject(DegToCntVId, self)

    @registerOp('GetDegSeqV')
    def GetDegSeqV(self, GraphId):
        Graph = self.Objects[GraphId]
        DegV = snap.TIntV()
        snap.GetDegSeqV(Graph, DegV)
        DegVId = self.__UpdateObjects(DegV, self.Lineage[GraphId])
        return RingoObject(DegVId, self)

    @registerOp('GetDegSeqV')
    def GetDegSeqV(self, GraphId):
        Graph = self.Objects[GraphId]
        InDegV = snap.TIntV()
        OutDegV = snap.TIntV()
        snap.GetDegSeqV(Graph, InDegV, OutDegV)
        InDegVId = self.__UpdateObjects(InDegV, self.Lineage[GraphId])
        OutDegVId = self.__UpdateObjects(OutDegV, self.Lineage[GraphId])
        return (RingoObject(InDegVId, self), RingoObject(OutDegVId, self))

    @registerOp('GetNodeInDegV')
    def GetNodeInDegV(self, GraphId):
        Graph = self.Objects[GraphId]
        NIdInDegV = snap.TIntPrV()
        snap.GetNodeInDegV(Graph, NIdInDegV)
        NIdInDegVId = self.__UpdateObjects(NIdInDegV, self.Lineage[GraphId])
        return RingoObject(NIdInDegVId, self)

    @registerOp('GetNodeOutDegV')
    def GetNodeOutDegV(self, GraphId):
        Graph = self.Objects[GraphId]
        NIdOutDegV = snap.TIntPrV()
        snap.GetNodeOutDegV(Graph, NIdOutDegV)
        NIdOutDegVId = self.__UpdateObjects(NIdOutDegV, self.Lineage[GraphId])
        return RingoObject(NIdOutDegVId, self)

    @registerOp('CntUniqUndirEdges', False)
    def CntUniqUndirEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        Count = snap.CntUniqUndirEdges(Graph)
        return Count

    @registerOp('CntUniqDirEdges', False)
    def CntUniqDirEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        Count = snap.CntUniqDirEdges(Graph)
        return Count

    @registerOp('CntUniqBiDirEdges', False)
    def CntUniqBiDirEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        Count = snap.CntUniqBiDirEdges(Graph)
        return Count

    @registerOp('CntSelfEdges', False)
    def CntSelfEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        Count = snap.CntSelfEdges(Graph)
        return Count

    @registerOp('GetUnDir')
    def GetUnDir(self, GraphId):
        Graph = self.Objects[GraphId]
        Ret = snap.GetUnDir(Graph)
        RetId = self.__UpdateObjects(Ret, self.Lineage[GraphId])
        return RingoObject(RetId, self)

    @registerOp('MakeUnDir')
    def MakeUnDir(self, GraphId):
        Graph = self.Objects[GraphId]
        snap.MakeUnDir(Graph)
        return RingoObject(GraphId, self)

    @registerOp('AddSelfEdges')
    def AddSelfEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        snap.AddSelfEdges(Graph)
        return RingoObject(GraphId, self)

    @registerOp('DelSelfEdges')
    def DelSelfEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        snap.DelSelfEdges(Graph)
        return RingoObject(GraphId, self)

    @registerOp('DelNodes')
    def DelNodes(self, GraphId, NIdVId):
        Graph = self.Objects[GraphId]
        NIdV = self.Objects[NIdVId]
        snap.DelNodes(Graph, NIdV)
        return RingoObject(GraphId, self)

    @registerOp('DelZeroDegNodes')
    def DelZeroDegNodes(self, GraphId):
        Graph = self.Objects[GraphId]
        snap.DelZeroDegNodes(Graph)
        return RingoObject(GraphId, self)

    @registerOp('DelDegKNodes')
    def DelDegKNodes(self, GraphId, OutDetK, InDegK):
        Graph = self.Objects[GraphId]
        snap.DelDegKNodes(Graph, OutDetK, InDegK)
        return RingoObject(GraphId, self)

    @registerOp('IsTree', False)
    def IsTree(self, GraphId):
        Graph = self.Objects[GraphId]
        Ret = snap.IsTree(Graph)
        return Ret

    @registerOp('GetTreeRootNId')
    def GetTreeRootNId(self, GraphId):
        Graph = self.Objects[GraphId]
        NId = snap.GetTreeRootNId(Graph)
        return NId

    @registerOp('GetTreeSig')
    def GetTreeSig(self, GraphId, RootNId):
        Graph = self.Objects[GraphId]
        Sig = snap.TIntV()
        snap.GetTreeSig(Graph, RootNId, Sig)
        SigId = self.__UpdateObjects(Sig, self.Lineage[GraphId])
        return RingoObject(SigId, self)

    @registerOp('GetTreeSig')
    def GetTreeSig(self, GraphId, RootNId):
        Graph = self.Objects[GraphId]
        Sig = snap.TIntV()
        NodeMap = snap.TIntPrV()
        snap.GetTreeSig(Graph, RootNId, Sig, NodeMap)
        SigId = self.__UpdateObjects(Sig, self.Lineage[GraphId])
        NodeMapId = self.__UpdateObjects(NodeMap, self.Lineage[GraphId])
        return (RingoObject(SigId, self), RingoObject(NodeMapId, self))

    @registerOp('GetAnf')
    def GetAnf(self, GraphId, SrcNId, MxDist, IsDir, NApprox = 32):
        Graph = self.Objects[GraphId]
        DistNbrsV = snap.TIntFltKdV()
        snap.GetAnf(Graph, DistNbrsV, SrcNId, MxDist, snap.TBool(IsDir), NApprox)
        DistNbrsVId = self.__UpdateObjects(DistNbrsV, self.Lineage[GraphId])
        return RingoObject(DistNbrsVId, self)

    @registerOp('GetAnf')
    def GetAnf(self, GraphId, MxDist, IsDir, NApprox = 32):
        Graph = self.Objects[GraphId]
        DistNbrsV = snap.TIntFltKdV()
        snap.GetAnf(Graph, DistNbrsV, MxDist, snap.TBool(IsDir), NApprox)
        DistNbrsVId = self.__UpdateObjects(DistNbrsV, self.Lineage[GraphId])
        return RingoObject(DistNbrsVId, self)

    @registerOp('GetAnfEffDiam', False)
    def GetAnfEffDiam(self, GraphId, IsDir, Percentile, NApprox):
        Graph = self.Objects[GraphId]
        Len = snap.GetAnfEffDiam(Graph, snap.TBool(IsDir), Percentile, NApprox)
        return Len

    @registerOp('GetAnfEffDiam', False)
    def GetAnfEffDiam(self, GraphId, NRuns = 1, NApprox = -1):
        Graph = self.Objects[GraphId]
        Len = snap.GetAnfEffDiam(Graph, NRuns, NApprox)
        return Len

    @registerOp('GetBfsTree')
    def GetBfsTree(self, GraphId, StartNId, FollowOut, FollowIn):
        Graph = self.Objects[GraphId]
        Tree = snap.GetBfsTree(Graph, StartNId, snap.TBool(FollowOut), snap.TBool(FollowIn))
        TreeId = self.__UpdateObjects(Tree, self.Lineage[GraphId])
        return RingoObject(TreeId, self)

    @registerOp('GetSubTreeSz', False)
    def GetSubTreeSz(self, GraphId, StartNId, FollowOut, FollowIn):
        Graph = self.Objects[GraphId]
        Sizes = snap.GetSubTreeSz(Graph, StartNId, snap.TBool(FollowOut), snap.TBool(FollowIn))
        return Sizes

    @registerOp('GetNodesAtHop')
    def GetNodesAtHop(self, GraphId, StartNId, Hop, IsDir):
        Graph = self.Objects[GraphId]
        NIdV = snap.TIntV()
        Count = snap.GetNodesAtHop(Graph, StartNId, Hop, NIdV, snap.TBool(IsDir))
        NIdVId = self.__UpdateObjects(NIdV, self.Lineage[GraphId])
        return (RingoObject(NIdVId, self), Count)

    @registerOp('GetNodesAtHops')
    def GetNodesAtHops(self, GraphId, StartNId, IsDir):
        Graph = self.Objects[GraphId]
        HopCntV = snap.TIntPrV()
        Count = snap.GetNodesAtHops(Graph, StartNId, HopCntV, snap.TBool(IsDir))
        HopCntVId = self.__UpdateObjects(HopCntV, self.Lineage[GraphId])
        return (RingoObject(HopCntVId, self), Count)

    @registerOp('GetShortPath', False)
    def GetShortPath(self, GraphId, SrcNId, DstNId, IsDir = False):
        Graph = self.Objects[GraphId]
        Len = snap.GetShortPath(Graph, SrcNId, DstNId, snap.TBool(IsDir))
        return Len

    @registerOp('GetShortPath')
    def GetShortPath(self, GraphId, SrcNId, IsDir = False, MaxDist = snap.TInt.Mx):
        Graph = self.Objects[GraphId]
        NIdToDistH = snap.TIntH()
        Len = snap.GetShortPath(Graph, SrcNId, NIdToDistH, snap.TBool(IsDir), MaxDist)
        NIdToDistHId = self.__UpdateObjects(NIdToDistH, self.Lineage[GraphId])
        return (RingoObject(NIdToDistHId, self), Len)

    @registerOp('GetBfsFullDiam', False)
    def GetBfsFullDiam(self, GraphId, NTestNodes, IsDir = False):
        Graph = self.Objects[GraphId]
        Diam = snap.GetBfsFullDiam(Graph, NTestNodes, snap.TBool(IsDir))
        return Diam

    @registerOp('GetBfsEffDiam', False)
    def GetBfsEffDiam(self, GraphId, NTestNodes, IsDir = False):
        Graph = self.Objects[GraphId]
        Diam = snap.GetBfsEffDiam(Graph, NTestNodes, snap.TBool(IsDir))
        return Diam

    @registerOp('GetDegreeCentr', False)
    def GetDegreeCentr(self, GraphId, NId):
        Graph = self.Objects[GraphId]
        Centr = snap.GetDegreeCentr(Graph, NId)
        return Centr

    @registerOp('GetFarnessCentr', False)
    def GetFarnessCentr(self, GraphId, NId):
        Graph = self.Objects[GraphId]
        Centr = snap.GetFarnessCentr(Graph, NId)
        return Centr

    @registerOp('GetClosenessCentr', False)
    def GetClosenessCentr(self, GraphId, NId):
        Graph = self.Objects[GraphId]
        Centr = snap.GetClosenessCentr(Graph, NId)
        return Centr

    @registerOp('GetBetweennessCentr')
    def GetBetweennessCentr(self, GraphId, NodeFrac = 1.0):
        Graph = self.Objects[GraphId]
        NodeBtwH = snap.TIntFltH()
        snap.GetBetweennessCentr(Graph, NodeBtwH, NodeFrac)
        NodeBtwHId = self.__UpdateObjects(NodeBtwH, self.Lineage[GraphId])
        return RingoObject(NodeBtwHId, self)

    @registerOp('GetBetweennessCentr')
    def GetBetweennessCentr(self, GraphId, NodeFrac = 1.0):
        Graph = self.Objects[GraphId]
        NodeBtwH = snap.TIntFltH()
        EdgeBtwH = snap.TIntPrFltH()
        snap.GetBetweennessCentr(Graph, NodeBtwH, EdgeBtwH, NodeFrac)
        NodeBtwHId = self.__UpdateObjects(NodeBtwH, self.Lineage[GraphId])
        EdgeBtwHId = self.__UpdateObjects(EdgeBtwH, self.Lineage[GraphId])
        return (RingoObject(NodeBtwHId, self), RingoObject(EdgeBtwHId, self))

    @registerOp('GetEigenVectorCentr')
    def GetEigenVectorCentr(self, GraphId, Eps = 1e-4, MaxIter = 100):
        Graph = self.Objects[GraphId]
        NIdEigenH = snap.TIntFltH()
        snap.GetEigenVectorCentr(Graph, NIdEigenH, Eps, MaxIter)
        NIdEigenHId = self.__UpdateObjects(NIdEigenH, self.Lineage[GraphId])
        return RingoObject(NIdEigenHId, self)

    @registerOp('GetNodeEcc', False)
    def GetNodeEcc(self, GraphId, NId, IsDir = False):
        Graph = self.Objects[GraphId]
        Ecc = snap.GetNodeEcc(Graph, NId, snap.TBool(IsDir))
        return Ecc

    @registerOp('CommunityGirvanNewman')
    def CommunityGirvanNewman(self, GraphId):
        Graph = self.Objects[GraphId]
        CmtyV = snap.TCnComV()
        Modularity = snap.CommunityGirvanNewman(Graph, CmtyV)
        CmtyVId = self.__UpdateObjects(CmtyV, self.Lineage[GraphId])
        return (RingoObject(CmtyVId, self), Modularity)

    @registerOp('CommunityCNM')
    def CommunityCNM(self, GraphId):
        Graph = self.Objects[GraphId]
        CmtyV = snap.TCnComV()
        Modularity = snap.CommunityCNM(Graph, CmtyV)
        CmtyVId = self.__UpdateObjects(CmtyV, self.Lineage[GraphId])
        return (RingoObject(CmtyVId, self), Modularity)

    @registerOp('GetModularity', False)
    def GetModularity(self, GraphId, NIdVId, GEdges = -1):
        Graph = self.Objects[GraphId]
        NIdV = self.Objects[NIdVId]
        Mod = snap.GetModularity(Graph, NIdV, GEdges)
        return Mod

    @registerOp('GetEdgesInOut', False)
    def GetEdgesInOut(self, GraphId, NIdVId):
        Graph = self.Objects[GraphId]
        NIdV = self.Objects[NIdVId]
        Ret = snap.GetEdgesInOut(Graph, NIdV)
        return Ret

    @registerOp('GetBiConSzCnt')
    def GetBiConSzCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        SzCntV = snap.TIntPrV()
        snap.GetBiConSzCnt(Graph, SzCntV)
        SzCntVId = self.__UpdateObjects(SzCntV, self.Lineage[GraphId])
        return RingoObject(SzCntVId, self)

    @registerOp('GetBiCon')
    def GetBiCon(self, GraphId):
        Graph = self.Objects[GraphId]
        BiCnComV = snap.TCnComV()
        snap.GetBiCon(Graph, BiCnComV)
        BiCnComVId = self.__UpdateObjects(BiCnComV, self.Lineage[GraphId])
        return RingoObject(BiCnComVId, self)

    @registerOp('GetArtPoints')
    def GetArtPoints(self, GraphId):
        Graph = self.Objects[GraphId]
        ArtNIdV = snap.TIntV()
        snap.GetArtPoints(Graph, ArtNIdV)
        ArtNIdVId = self.__UpdateObjects(ArtNIdV, self.Lineage[GraphId])
        return RingoObject(ArtNIdVId, self)

    @registerOp('GetEdgeBridges')
    def GetEdgeBridges(self, GraphId):
        Graph = self.Objects[GraphId]
        EdgeV = snap.TIntPrV()
        snap.GetEdgeBridges(Graph, EdgeV)
        EdgeVId = self.__UpdateObjects(EdgeV, self.Lineage[GraphId])
        return RingoObject(EdgeVId, self)

    @registerOp('Get1CnComSzCnt')
    def Get1CnComSzCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        SzCntV = snap.TIntPrV()
        snap.Get1CnComSzCnt(Graph, SzCntV)
        SzCntVId = self.__UpdateObjects(SzCntV, self.Lineage[GraphId])
        return RingoObject(SzCntVId, self)

    @registerOp('Get1CnCom')
    def Get1CnCom(self, GraphId):
        Graph = self.Objects[GraphId]
        Cn1ComV = snap.TCnComV()
        snap.Get1CnCom(Graph, Cn1ComV)
        Cn1ComVId = self.__UpdateObjects(Cn1ComV, self.Lineage[GraphId])
        return RingoObject(Cn1ComVId, self)

    @registerOp('GetMxBiCon')
    def GetMxBiCon(self, GraphId):
        Graph = self.Objects[GraphId]
        BiCon = snap.GetMxBiCon(Graph)
        BiConId = self.__UpdateObjects(BiCon, self.Lineage[GraphId])
        return RingoObject(BiConId, self)

    @registerOp('GetNodeWcc')
    def GetNodeWcc(self, GraphId, NId):
        Graph = self.Objects[GraphId]
        CnCom = snap.TIntV()
        snap.GetNodeWcc(Graph, NId, CnCom)
        CnComId = self.__UpdateObjects(CnCom, self.Lineage[GraphId])
        return RingoObject(CnComId, self)

    @registerOp('IsConnected', False)
    def IsConnected(self, GraphId):
        Graph = self.Objects[GraphId]
        isCon = snap.IsConnected(Graph)
        return isCon

    @registerOp('IsWeaklyConn', False)
    def IsWeaklyConn(self, GraphId):
        Graph = self.Objects[GraphId]
        isCon = snap.IsWeaklyConn(Graph)
        return isCon

    @registerOp('GetWccSzCnt')
    def GetWccSzCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        WccSzzCnt = snap.TIntPrV()
        snap.GetWccSzCnt(Graph, WccSzzCnt)
        WccSzzCntId = self.__UpdateObjects(WccSzzCnt, self.Lineage[GraphId])
        return RingoObject(WccSzzCntId, self)

    @registerOp('GetWccs')
    def GetWccs(self, GraphId):
        Graph = self.Objects[GraphId]
        CnComV = snap.TCnComV()
        snap.GetWccs(Graph, CnComV)
        CnComVId = self.__UpdateObjects(CnComV, self.Lineage[GraphId])
        return RingoObject(CnComVId, self)

    @registerOp('GetSccSzCnt')
    def GetSccSzCnt(self, GraphId):
        Graph = self.Objects[GraphId]
        SccSzCnt = snap.TIntPrV()
        snap.GetSccSzCnt(Graph, SccSzCnt)
        SccSzCntId = self.__UpdateObjects(SccSzCnt, self.Lineage[GraphId])
        return RingoObject(SccSzCntId, self)

    @registerOp('GetSccs')
    def GetSccs(self, GraphId):
        Graph = self.Objects[GraphId]
        CnComV = snap.TCnComV()
        snap.GetSccs(Graph, CnComV)
        CnComVId = self.__UpdateObjects(CnComV, self.Lineage[GraphId])
        return RingoObject(CnComVId, self)

    @registerOp('GetMxWccSz', False)
    def GetMxWccSz(self, GraphId):
        Graph = self.Objects[GraphId]
        Size = snap.GetMxWccSz(Graph)
        return Size

    @registerOp('GetMxSccSz', False)
    def GetMxSccSz(self, GraphId):
        Graph = self.Objects[GraphId]
        Size = snap.GetMxSccSz(Graph)
        return Size

    @registerOp('GetMxWcc')
    def GetMxWcc(self, GraphId):
        Graph = self.Objects[GraphId]
        Graph = snap.GetMxWcc(Graph)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphId])
        return RingoObject(GraphId, self)

    @registerOp('GetMxScc')
    def GetMxScc(self, GraphId):
        Graph = self.Objects[GraphId]
        Graph = snap.GetMxScc(Graph)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphId])
        return RingoObject(GraphId, self)

    @registerOp('PrintInfo', False)
    def PrintInfo(self, GraphId, Desc, OutFNm = "", Fast = True):
        Graph = self.Objects[GraphId]
        snap.PrintInfo(Graph, Desc, OutFNm, snap.TBool(Fast))

    @registerOp('GetTriads', False)
    def GetTriads(self, GraphId, SampleNodes = -1):
        Graph = self.Objects[GraphId]
        NumTri = snap.GetTriads(Graph, SampleNodes)
        return NumTri

    @registerOp('GetKCoreNodes')
    def GetKCoreNodes(self, GraphId):
        Graph = self.Objects[GraphId]
        CoreIdSzV = snap.TIntPrV()
        Count = snap.GetKCoreNodes(Graph, CoreIdSzV)
        CoreIdSzVId = self.__UpdateObjects(CoreIdSzV, self.Lineage[GraphId])
        return (RingoObject(CoreIdSzVId, self), Count)

    @registerOp('GetKCoreEdges')
    def GetKCoreEdges(self, GraphId):
        Graph = self.Objects[GraphId]
        CoreIdSzV = snap.TIntPrV()
        Count = snap.GetKCoreEdges(Graph, CoreIdSzV)
        CoreIdSzVId = self.__UpdateObjects(CoreIdSzV, self.Lineage[GraphId])
        return (RingoObject(CoreIdSzVId, self), Count)

    @registerOp('GenRndDegK')
    def GenRndDegK(self, Nodes, NodeDeg, NSwitch = 100, Rnd = snap.TRnd()):
        Graph = snap.GenRndDegK(Nodes, NodeDeg, NSwitch, Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenRndPowerLaw')
    def GenRndPowerLaw(self, Nodes, PowerExp, ConfModel = True, Rnd = snap.TRnd()):
        Graph = snap.GenRndPowerLaw(Nodes, PowerExp, snap.TBool(ConfModel), Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenDegSeq')
    def GenDegSeq(self, DegSeqVId, Rnd = snap.TRnd()):
        DegSeqV = self.Objects[DegSeqVId]
        Graph = snap.GenDegSeq(DegSeqV, Rnd)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[DegSeqVId])
        return RingoObject(GraphId, self)

    @registerOp('GenConfModel')
    def GenConfModel(self, GraphId):
        Graph = self.Objects[GraphId]
        Ret = snap.GenConfModel(Graph)
        RetId = self.__UpdateObjects(Ret, self.Lineage[GraphId])
        return RingoObject(RetId, self)

    @registerOp('GenRewire')
    def GenRewire(self, GraphId, NSwitch = 100, Rnd = snap.TRnd()):
        Graph = self.Objects[GraphId]
        Ret = snap.GenRewire(Graph, NSwitch, Rnd)
        RetId = self.__UpdateObjects(Ret, self.Lineage[GraphId])
        return RingoObject(RetId, self)

    @registerOp('GenPrefAttach')
    def GenPrefAttach(self, Nodes, NodeOutDeg, Rnd = snap.TRnd()):
        Graph = snap.GenPrefAttach(Nodes, NodeOutDeg, Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenConfModel')
    def GenConfModel(self, GraphId):
        Graph = self.Objects[GraphId]
        Ret = snap.GenConfModel(Graph)
        RetId = self.__UpdateObjects(Ret, self.Lineage[GraphId])
        return RingoObject(RetId, self)

    @registerOp('GenGeoPrefAttach')
    def GenGeoPrefAttach(self, NumNodes, NumEdges, Beta, Rnd = snap.TRnd()):
        Graph = snap.GenGeoPrefAttach(NumNodes, NumEdges, Beta, Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenSmallWorld')
    def GenSmallWorld(self, Nodes, NodeOutDeg, RewireProb, Rnd = snap.TRnd()):
        Graph = snap.GenSmallWorld(Nodes, NodeOutDeg, RewireProb, Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenForestFire')
    def GenForestFire(self, Nodes, FwdProb, BckProb):
        Graph = snap.GenForestFire(Nodes, FwdProb, BckProb)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenCopyModel')
    def GenCopyModel(self, Nodes, Beta, Rnd = snap.TRnd()):
        Graph = snap.GenCopyModel(Nodes, Beta, Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenRMat')
    def GenRMat(self, Nodes, Edges, A, B, C, Rnd = snap.TRnd()):
        Graph = snap.GenRMat(Nodes, Edges, A, B, C, Rnd)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenRMatEpinions')
    def GenRMatEpinions(self):
        Graph = snap.GenRMatEpinions()
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('GenGrid')
    def GenGrid(self, GraphTypeId, Rows, Cols, IsDir = True):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenGrid(GraphType, Rows, Cols, snap.TBool(IsDir))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('GenStar')
    def GenStar(self, GraphTypeId, Nodes, IsDir = True):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenStar(GraphType, Nodes, snap.TBool(IsDir))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('GenCircle')
    def GenCircle(self, GraphTypeId, Nodes, OutDegree, IsDir = True):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenCircle(GraphType, Nodes, OutDegree, snap.TBool(IsDir))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('GenFull')
    def GenFull(self, GraphTypeId, Nodes):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenFull(GraphType, Nodes)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('GenTree')
    def GenTree(self, GraphTypeId, Fanout, Levels, IsDir = True, ChildPointsToParent = True):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenTree(GraphType, Fanout, Levels, snap.TBool(IsDir), snap.TBool(ChildPointsToParent))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('GenBaraHierar')
    def GenBaraHierar(self, GraphTypeId, Levels, IsDir = True):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenBaraHierar(GraphType, Levels, snap.TBool(IsDir))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('GenRndGnm')
    def GenRndGnm(self, GraphTypeId, Nodes, Edges, IsDir = True, Rnd = snap.TRnd()):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.GenRndGnm(GraphType, Nodes, Edges, snap.TBool(IsDir), Rnd)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('LoadDyNet')
    def LoadDyNet(self, FNm):
        Graph = snap.LoadDyNet(FNm)
        GraphId = self.__UpdateObjects(Graph, [])
        return RingoObject(GraphId, self)

    @registerOp('LoadEdgeList')
    def LoadEdgeList(self, GraphTypeId, InFNm, SrcColId, DstColId, Separator):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.LoadEdgeList(GraphType, InFNm, SrcColId, DstColId, Separator)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('LoadEdgeList')
    def LoadEdgeList(self, GraphTypeId, InFNm, SrcColId, DstColId):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.LoadEdgeList(GraphType, InFNm, SrcColId, DstColId)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('LoadEdgeListStr')
    def LoadEdgeListStr(self, GraphTypeId, InFNm, SrcColId, DstColId):
        GraphType = self.Objects[GraphTypeId]
        StrToNIdH = snap.TStrIntH()
        Graph = snap.LoadEdgeListStr(GraphType, InFNm, SrcColId, DstColId, StrToNIdH)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        StrToNIdHId = self.__UpdateObjects(StrToNIdH, self.Lineage[GraphTypeId])
        return (RingoObject(GraphId, self), RingoObject(StrToNIdHId, self))

    @registerOp('LoadEdgeListStr')
    def LoadEdgeListStr(self, GraphTypeId, InFNm, SrcColId, DstColId):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.LoadEdgeListStr(GraphType, InFNm, SrcColId, DstColId)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('LoadConnList')
    def LoadConnList(self, GraphTypeId, InFNm):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.LoadConnList(GraphType, InFNm)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)

    @registerOp('LoadConnListStr')
    def LoadConnListStr(self, GraphTypeId, InFNm):
        GraphType = self.Objects[GraphTypeId]
        StrToNIdH = snap.TStrIntH()
        Graph = snap.LoadConnListStr(GraphType, InFNm, StrToNIdH)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        StrToNIdHId = self.__UpdateObjects(StrToNIdH, self.Lineage[GraphTypeId])
        return (RingoObject(GraphId, self), RingoObject(StrToNIdHId, self))

    @registerOp('LoadPajek')
    def LoadPajek(self, GraphTypeId, InFNm):
        GraphType = self.Objects[GraphTypeId]
        Graph = snap.LoadPajek(GraphType, InFNm)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId])
        return RingoObject(GraphId, self)
	
	# Save graph to Text file
    @registerOp('SaveEdgeList', False)
    def SaveEdgeList(self, GraphId, OutFNm, Desc = ""):
        Graph = self.Objects[GraphId]
        snap.SaveEdgeList(Graph, OutFNm, Desc)

    @registerOp('SavePajek', False)
    def SavePajek(self, GraphId, OutFNm):
        Graph = self.Objects[GraphId]
        snap.SavePajek(Graph, OutFNm)

    @registerOp('SavePajek', False)
    def SavePajek(self, GraphId, OutFNm, NIdColorHId):
        Graph = self.Objects[GraphId]
        NIdColorH = self.Objects[NIdColorHId]
        snap.SavePajek(Graph, OutFNm, NIdColorH)

    @registerOp('SavePajek', False)
    def SavePajek(self, GraphId, OutFNm, NIdColorHId, NIdLabelHId):
        Graph = self.Objects[GraphId]
        NIdColorH = self.Objects[NIdColorHId]
        NIdLabelH = self.Objects[NIdLabelHId]
        snap.SavePajek(Graph, OutFNm, NIdColorH, NIdLabelH)

    @registerOp('SavePajek', False)
    def SavePajek(self, GraphId, OutFNm, NIdColorHId, NIdLabelHId, EIdColorHId):
        Graph = self.Objects[GraphId]
        NIdColorH = self.Objects[NIdColorHId]
        NIdLabelH = self.Objects[NIdLabelHId]
        EIdColorH = self.Objects[EIdColorHId]
        snap.SavePajek(Graph, OutFNm, NIdColorH, NIdLabelH, EIdColorH)

    @registerOp('SaveMatlabSparseMtx', False)
    def SaveMatlabSparseMtx(self, GraphId, OutFNm):
        Graph = self.Objects[GraphId]
        snap.SaveMatlabSparseMtx(Graph, OutFNm)

    @registerOp('SaveGViz', False)
    def SaveGViz(self, GraphId, OutFNm, Desc, NIdLabelHId):
        Graph = self.Objects[GraphId]
        NIdLabelH = self.Objects[NIdLabelHId]
        snap.SaveGViz(Graph, OutFNm, Desc, NIdLabelH)

    @registerOp('SaveGViz', False)
    def SaveGViz(self, GraphId, OutFNm, Desc, NodeLabels, NIdColorHId):
        Graph = self.Objects[GraphId]
        NIdColorH = self.Objects[NIdColorHId]
        snap.SaveGViz(Graph, OutFNm, Desc, snap.TBool(NodeLabels), NIdColorH)

    @registerOp('GetSngVals')
    def GetSngVals(self, GraphId, SngVals):
        Graph = self.Objects[GraphId]
        SngValV = snap.TFltV()
        snap.GetSngVals(Graph, SngVals, SngValV)
        SngValVId = self.__UpdateObjects(SngValV, self.Lineage[GraphId])
        return RingoObject(SngValVId, self)

    @registerOp('GetSngVec')
    def GetSngVec(self, GraphId):
        Graph = self.Objects[GraphId]
        LeftSV = snap.TFltV()
        RightSV = snap.TFltV()
        snap.GetSngVec(Graph, LeftSV, RightSV)
        LeftSVId = self.__UpdateObjects(LeftSV, self.Lineage[GraphId])
        RightSVId = self.__UpdateObjects(RightSV, self.Lineage[GraphId])
        return (RingoObject(LeftSVId, self), RingoObject(RightSVId, self))

    @registerOp('GetEigVals')
    def GetEigVals(self, GraphId, EigVals):
        Graph = self.Objects[GraphId]
        EigValV = snap.TFltV()
        snap.GetEigVals(Graph, EigVals, EigValV)
        EigValVId = self.__UpdateObjects(EigValV, self.Lineage[GraphId])
        return RingoObject(EigValVId, self)

    @registerOp('GetEigVec')
    def GetEigVec(self, GraphId):
        Graph = self.Objects[GraphId]
        EigVecV = snap.TFltV()
        snap.GetEigVec(Graph, EigVecV)
        EigVecVId = self.__UpdateObjects(EigVecV, self.Lineage[GraphId])
        return RingoObject(EigVecVId, self)

    @registerOp('GetInvParticipRate')
    def GetInvParticipRate(self, GraphId, EigVecs, TimeLimit):
        Graph = self.Objects[GraphId]
        EigValIprV = snap.TFltPrV()
        snap.GetInvParticipRate(Graph, EigVecs, TimeLimit, EigValIprV)
        EigValIprVId = self.__UpdateObjects(EigValIprV, self.Lineage[GraphId])
        return RingoObject(EigValIprVId, self)

    @registerOp('DrawGViz')
    def DrawGViz(self, GraphId, LayoutId, PItFNm, Desc, NodeLabelHId):
        Graph = self.Objects[GraphId]
        Layout = self.Objects[LayoutId]
        NodeLabelH = self.Objects[NodeLabelHId]
        snap.DrawGViz(Graph, Layout, PItFNm, Desc, NodeLabelH)

    @registerOp('DrawGViz')
    def DrawGViz(self, GraphId, LayoutId, PItFNm, Desc = "", NodeLabels = False, NIdColorH = snap.TIntStrH()):
        Graph = self.Objects[GraphId]
        Layout = self.Objects[LayoutId]
        snap.DrawGViz(Graph, Layout, PItFNm, Desc, snap.TBool(NodeLabels), NIdColorH)

    @registerOp('GetKCore')
    def GetKCore(self, GraphId, K):
        Graph = self.Objects[GraphId]
        Core = snap.GetKCore(Graph, K)
        CoreId = self.__UpdateObjects(Core, self.Lineage[GraphId])
        return RingoObject(CoreId, self)

    @registerOp('PlotEigValRank', False)
    def PlotEigValRank(self, GraphId, EigVals, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotEigValRank(Graph, EigVals, FNmPref, DescStr)

    @registerOp('PlotEigValDistr', False)
    def PlotEigValDistr(self, GraphId, EigVals, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotEigValDistr(Graph, EigVals, FNmPref, DescStr)

    @registerOp('PlotInvParticipRat', False)
    def PlotInvParticipRat(self, GraphId, EigVecs, TimeLimit, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotInvParticipRat(Graph, EigVecs, TimeLimit, FNmPref, DescStr)

    @registerOp('PlotSngValRank', False)
    def PlotSngValRank(self, GraphId, SngVals, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotSngValRank(Graph, SngVals, FNmPref, DescStr)

    @registerOp('PlotSngValDistr', False)
    def PlotSngValDistr(self, GraphId, SngVals, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotSngValDistr(Graph, SngVals, FNmPref, DescStr)

    @registerOp('PlotSngVec', False)
    def PlotSngVec(self, GraphId, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotSngVec(Graph, FNmPref, DescStr)

    @registerOp('PlotInDegDistr', False)
    def PlotInDegDistr(self, GraphId, FNmPref, DescStr = "", PlotCCdf = False, PowerFit = False):
        Graph = self.Objects[GraphId]
        snap.PlotInDegDistr(Graph, FNmPref, DescStr, snap.TBool(PlotCCdf), snap.TBool(PowerFit))

    @registerOp('PlotOutDegDistr', False)
    def PlotOutDegDistr(self, GraphId, FNmPref, DescStr = "", PlotCCdf = False, PowerFit = False):
        Graph = self.Objects[GraphId]
        snap.PlotOutDegDistr(Graph, FNmPref, DescStr, snap.TBool(PlotCCdf), snap.TBool(PowerFit))

    @registerOp('PlotWccDistr', False)
    def PlotWccDistr(self, GraphId, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotWccDistr(Graph, FNmPref, DescStr)

    @registerOp('PlotSccDistr', False)
    def PlotSccDistr(self, GraphId, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotSccDistr(Graph, FNmPref, DescStr)

    @registerOp('PlotClustCf', False)
    def PlotClustCf(self, GraphId, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotClustCf(Graph, FNmPref, DescStr)

    @registerOp('PlotHops', False)
    def PlotHops(self, GraphId, FNmPref, DescStr = "", IsDir = False, NApprox = 32):
        Graph = self.Objects[GraphId]
        snap.PlotHops(Graph, FNmPref, DescStr, snap.TBool(IsDir), NApprox)

    @registerOp('PlotShortPathDistr', False)
    def PlotShortPathDistr(self, GraphId, FNmPref, DescStr = "", TestNodes = snap.TInt.Mx):
        Graph = self.Objects[GraphId]
        snap.PlotShortPathDistr(Graph, FNmPref, DescStr, TestNodes)

    @registerOp('PlotKCoreNodes', False)
    def PlotKCoreNodes(self, GraphId, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotKCoreNodes(Graph, FNmPref, DescStr)

    @registerOp('PlotKCoreEdges', False)
    def PlotKCoreEdges(self, GraphId, FNmPref, DescStr = ""):
        Graph = self.Objects[GraphId]
        snap.PlotKCoreEdges(Graph, FNmPref, DescStr)

    @registerOp('ConvertGraph')
    def ConvertGraph(self, GraphTypeId, InGraphId, RenumberNodes = False):
        GraphType = self.Objects[GraphTypeId]
        InGraph = self.Objects[InGraphId]
        OutGraph = snap.ConvertGraph(GraphType, InGraph, snap.TBool(RenumberNodes))
        OutGraphId = self.__UpdateObjects(OutGraph, self.Lineage[GraphTypeId] + self.Lineage[InGraphId])
        return RingoObject(OutGraphId, self)

    @registerOp('ConvertESubGraph')
    def ConvertESubGraph(self, GraphTypeId, InGraphId, EIdVId, RenumberNodes = False):
        GraphType = self.Objects[GraphTypeId]
        InGraph = self.Objects[InGraphId]
        EIdV = self.Objects[EIdVId]
        Graph = snap.ConvertESubGraph(GraphType, InGraph, EIdV, snap.TBool(RenumberNodes))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId] + self.Lineage[InGraphId] + self.Lineage[EIdVId])
        return RingoObject(GraphId, self)

    @registerOp('ConvertSubgraph')
    def ConvertSubgraph(self, GraphTypeId, InGraphId, NIdVId, RenumberNodes = False):
        GraphType = self.Objects[GraphTypeId]
        InGraph = self.Objects[InGraphId]
        NIdV = self.Objects[NIdVId]
        Graph = snap.ConvertSubgraph(GraphType, InGraph, NIdV, snap.TBool(RenumberNodes))
        GraphId = self.__UpdateObjects(Graph, self.Lineage[GraphTypeId] + self.Lineage[InGraphId] + self.Lineage[NIdVId])
        return RingoObject(GraphId, self)

    @registerOp('GetClustCf')
    def GetClustCf(self, GraphId, SampleNodes = -1):
        Graph = self.Objects[GraphId]
        DegToCCfV = snap.TFltPrV()
        Ret = snap.GetClustCf(Graph, DegToCCfV, SampleNodes)
        DegToCCfVId = self.__UpdateObjects(DegToCCfV, self.Lineage[GraphId])
        return (RingoObject(DegToCCfVId, self), Ret)

    @registerOp('GetClustCf', False)
    def GetClustCf(self, GraphId, SampleNodes = -1):
        Graph = self.Objects[GraphId]
        Ret = snap.GetClustCf(Graph, SampleNodes)
        return Ret

    @registerOp('GetCmnNbrs')
    def GetCmnNbrs(self, GraphId, NId1, NId2):
        Graph = self.Objects[GraphId]
        NbrV = snap.TIntV()
        Ret = snap.GetCmnNbrs(Graph, NId1, NId2, NbrV)
        NbrVId = self.__UpdateObjects(NbrV, self.Lineage[GraphId])
        return (RingoObject(NbrVId, self), Ret)

    @registerOp('GetESubGraph')
    def GetESubGraph(self, InGraphId, EIdVId):
        InGraph = self.Objects[InGraphId]
        EIdV = self.Objects[EIdVId]
        Graph = snap.GetESubGraph(InGraph, EIdV)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[InGraphId] + self.Lineage[EIdVId])
        return RingoObject(GraphId, self)

    @registerOp('GetNodeClustCf', False)
    def GetNodeClustCf(self, GraphId, NId):
        Graph = self.Objects[GraphId]
        Ret = snap.GetNodeClustCf(Graph, NId)
        return Ret

    @registerOp('GetNodeClustCf')
    def GetNodeClustCf(self, GraphId):
        Graph = self.Objects[GraphId]
        NIdCCfH = snap.TIntFltH()
        snap.GetNodeClustCf(Graph, NIdCCfH)
        NIdCCfHId = self.__UpdateObjects(NIdCCfH, self.Lineage[GraphId])
        return RingoObject(NIdCCfHId, self)

    @registerOp('GetNodeTriads', False)
    def GetNodeTriads(self, GraphId, NId):
        Graph = self.Objects[GraphId]
        Ret = snap.GetNodeTriads(Graph, NId)
        return Ret

    @registerOp('GetRndESubGraph')
    def GetRndESubGraph(self, InGraphId, NumEdges):
        InGraph = self.Objects[InGraphId]
        Graph = snap.GetRndESubGraph(InGraph, NumEdges)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[InGraphId])
        return RingoObject(GraphId, self)

    @registerOp('GetRndSubGraph')
    def GetRndSubGraph(self, InGraphId, NumNodes):
        InGraph = self.Objects[InGraphId]
        Graph = snap.GetRndSubGraph(InGraph, NumNodes)
        GraphId = self.__UpdateObjects(Graph, self.Lineage[InGraphId])
        return RingoObject(GraphId, self)

    @registerOp('GetTriadEdges', False)
    def GetTriadEdges(self, GraphId, SampleEdges):
        Graph = self.Objects[GraphId]
        Ret = snap.GetTriadEdges(Graph, SampleEdges)
        return Ret

    @registerOp('GetTriadParticip')
    def GetTriadParticip(self, GraphId):
        Graph = self.Objects[GraphId]
        TriadCntV = snap.TIntPrV()
        snap.GetTriadParticip(Graph, TriadCntV)
        TriadCntVId = self.__UpdateObjects(TriadCntV, self.Lineage[GraphId])
        return RingoObject(TriadCntVId, self)

