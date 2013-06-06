from value import Value

class Aggregator:
	
	def __init__(self,names):
		self.aggregator = [{
			'sum':sum,
			'avg':(lambda l: sum(l)/len(l)),
			'min':min,
			'max':max,
			'cnt':len,
			'list':lambda x: x
		}[name] for name in names]
		self.length = len(names)

	def calc(self,values):
		# Transform list of rows in list of columns
		cols = zip(*values)
		return [Value(val=agg(col)) for agg,col in zip(self.aggregator,cols)]