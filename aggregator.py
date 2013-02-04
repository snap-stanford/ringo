from value import Value

class Aggregator:
	
	def __init__(self,name):
		self.aggregator = {
			'sum':sum,
			'avg':(lambda l: sum(l)/len(l)),
			'min':min,
			'max':max,
			'cnt':len
		}[name]

	def calc(self,l):
		return Value(val=self.aggregator(l))