from operator import lt, le, eq, ne, ge, gt

class Condition:
	def __init__(self, op, value):
		self.op = {'<':lt,'<=':le,'==':eq,'!=':ne,'>=':ge,'>':gt}[op]
		self.value = value
		
	def getOp(self):
		return self.op

	def eval(self, value):
		return self.op(value,self.value)