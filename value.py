
import time

class Value:
	
	def __init__(self, strval=None, val=None):
		# If the val argument is used, the constructor will not try to infer the type
		self.val = val
		if not strval is None:
			if strval == '':
				self.val = None
			try:
				self.val = float(strval)
			except ValueError:
				try:
					# TODO: use datetime module to keep milliseconds
					spl = strval.split('.')
					self.val = time.strptime(spl[0],'%Y-%m-%dT%H:%M:%S')
				except ValueError:
					self.val = strval

	def getType(self):
		return type(self.val)

	def __repr__(self):
		return str(self)

	def __str__(self):
		return unicode(self).encode('unicode-escape')

	def __unicode__(self):
		if self.val is None:
			return ''
		elif type(self.val) is time.struct_time:
			return time.strftime('%Y-%m-%dT%H:%M:%S',self.val)
		else:
			return unicode(self.val)

	def __lt__(self, other):
		if self.__class__ == other.__class__:
			return self.val < other.val
		else:
			return self.val < other

	def __le__(self, other):
		if self.__class__ == other.__class__:
			return self.val <= other.val
		else:
			return self.val <= other

	def __eq__(self, other):
		if self.__class__ == other.__class__:
			return self.val == other.val
		else:
			return self.val == other

	def __ne__(self, other):
		if self.__class__ == other.__class__:
			return self.val != other.val
		else:
			return self.val != other

	def __ge__(self, other):
		if self.__class__ == other.__class__:
			return self.val >= other.val
		else:
			return self.val >= other

	def __gt__(self, other):
		if self.__class__ == other.__class__:
			return self.val > other.val
		else:
			return self.val > other

	def __add__(self, other):
		# TODO: do we want this behavior for strings and dates?
		if self.__class__ == other.__class__:
			return Value(val=self.val + other.val)
		else:
			return Value(val=self.val + other)

	def __sub__(self, other):
		if self.__class__ == other.__class__:
			return Value(val=self.val - other.val)
		else:
			return Value(val=self.val - other)

	def __mul__(self, other):
		if self.__class__ == other.__class__:
			return Value(val=self.val * other.val)
		else:
			return Value(val=self.val * other)

	def __div__(self, other):
		if self.__class__ == other.__class__:
			return Value(val=self.val / other.val)
		else:
			return Value(val=self.val / other)

	def __radd__(self, other):
		if self.__class__ == other.__class__:
			return Value(val=self.val + other.val)
		else:
			return Value(val=self.val + other)

	# TODO: Remove these functions

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
