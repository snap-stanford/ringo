from snap import *
from time import gmtime, strftime

class ringo(object):
    dataTypes = ['int', 'float', 'string']
    def __init__(self):
        # mapping between table names and table objects
        self.Tables = {}
        # an operation record has the form: <id (int), type (string), result table name (string), argument list (as used in python interface; table names are used for table arguments), time stamp>
        self.Operations = [] 
        # mapping between a table (name/id) and the sequence of operation ids that led to it
        self.Lineage = {}
        # mapping between network names and network objects
        self.Networks = {}
        # mapping between a table (name/id) and the names of the networks that originated from it
        self.TableToNetworks = {}
        self.Context = TTableContext.New()
        
    # Use case:
    # S = {'name':'string', 'age':'int', 'weight':'float'}
    # ringo.LoadTableTSV('My Table', S, 'table.tsv')
    # ringo.LoadTableTSV('My Table', S, 'table.tsv', [0,1]) if we want to load only columns 'name' and 'age'
    def LoadTableTSV(self, TableName, Schema, InFnm, RelevantCols = [], SeparatorChar = '\t', HasTitleLine = True):
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
        
        # Load input and create new TTable object
        T = TTable.LoadSS(TableName, S, InFnm, StringVals, RC, SeparatorChar, HasTitleLine)
        
        # update engine's data structures
        self.Tables[TableName] = T
        args = (TableName, Schema, InFnm, RelevantCols, SeparatorChar, HasTitleLine)
        OpId = len(Operations)
        Op = (OpId, 'load tsv', TableName, args, strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
        self.Operations.append(Op)
        Lineage[TableName] = [OpId]
        
    def SaveTableTSV(self, TableName, OutFnm):
        T = Tables[TableName]
        T.SaveSS(OutFnm)
        Op = (len(Operations), 'save tsv', TableName, (TableName, OutFnm), strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
        self.Operations.append(Op)
    
    def GetOpType(self, OpId):
        return Operations[OpId][1]
        
        
        
            