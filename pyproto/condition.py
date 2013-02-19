from operator import lt, le, eq, ne, ge, gt

class Condition:
    def __init__(self, attr, op, value):
        self.attribute = attr
        self.op = {'<':lt,'<=':le,'==':eq,'!=':ne,'>=':ge,'>':gt}[op]
        self.value = value
        self.index = None

    def getOp(self):
        return self.op

    def eval(self, row):
        return self.op(row[self.index],self.value)

    def configureForTable(self, table):
        self.index = table.columns.index(self.attribute)