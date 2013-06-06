from operator import lt, le, eq, ne, ge, gt

class ConditionNotConfiguredError(Exception):
    def __init__(self,message):
        self.message = message
    def __repr__(self):
        return repr(self.message)

class Condition:
    def __init__(self, attr, op, value):
        self.attribute = attr
        self.op = {'<':lt,'<=':le,'==':eq,'!=':ne,'>=':ge,'>':gt}[op]
        self.value = value
        self.idx = None
        self.pos = None

    def getOp(self):
        return self.op

    def eval(self, row):
        if self.idx is None:
            raise ConditionNotConfiguredError('The condition must be configured to be used with a particular table.')
        return self.op(row[self.pos],self.value)

    def configureForTable(self, table):
        self.idx = table.getIndex(self.attribute)
        self.pos = table.columns.index(self.idx)