
class Value:
	
	def __init__(self, val):
		self. val = val

	def equals(self, other):
		return self.val == other.val

	def lessThan(self, other):
		return self.val < other.val

	def greaterThan(self, other):
		return self.val > other.val		

	def lessThanOrEqual(self, other):
		return self.val <= other.val

	def greaterThanOrEqual(self, other):
		return self.val >= other.val

	def compare(self, other, op):
		if (op == "=="):
			return self.equals(other)
		if (op == ">"):
			return self.greaterThan(other)
		if (op == ">="):
			return self.greaterThanOrEqual(other)
		if (op == "<"):
			return self.lessThan(other)
		if (op == "<="):
			return self.lessThanOrEqual(other)
