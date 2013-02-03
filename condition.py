
class Condition:
	def __init__(self, op, value):
		self.op = op
		self.value = value
		
	def getOp(self):
		return self.op

	def eval(self, value2):
		value.compare(value2, self.op);