import csv
import os
import condition
import string
import value
import aggregator
import pdb
import types
import copy
import util
import gsql
from operator import __and__
from value import Value
from xml.dom.minidom import parse

class AttributeStore:
	def __init__(self):
		self.attrDict = {}
		self.idxDict = {}
		self.types = {}
		self.currIdx = 0
	def addAttr(self,name,ty):
		self.attrDict[self.currIdx] = name
		self.types[self.currIdx] = ty
		if not name in self.idxDict:
			self.idxDict[name] = []
		self.idxDict[name].append(self.currIdx)
		self.currIdx += 1
		return self.currIdx - 1
	def getIndexes(self,attr):
		return self.idxDict[attr]
	def getAttr(self,idx):
		return self.attrDict[idx]
	def getType(self,idx):
		return self.types[idx]
	def setName(self,idx,name):
		self.idxDict[self.attrDict[idx]].remove(idx)
		self.attrDict[idx] = name
		if not self.idxDict[name]:
			self.idxDict[name] = []
		self.idxDict[name].append(idx)
	def setType(self,idx,ty):
		self.types[i] = ty
	def copy(self):
		attrStore = AttributeStore()
		attrStore.attrDict = copy.deepcopy(self.attrDict)
		attrStore.idxDict = copy.deepcopy(self.idxDict)
		attrStore.types = copy.deepcopy(self.types)
		attrStore.currIdx = self.currIdx
		return attrStore

class TableStructureError(Exception):
	def __init__(self,message):
		self.message = message
	def __repr__(self):
		return repr(self.message)
class TableAttrNotFoundError(Exception):
	def __init__(self,message):
		self.message = message
	def __repr__(self):
		return repr(self.message)

class Table:

	defaultAttributeStore = AttributeStore()

	def __init__(self, filename=None, name=None, attrStore=None):
		self.columns = []
		self.data = []
		self.dumpcnt = 0
		self.name = None
		if attrStore is None:
			 # Attribute Store is shared between tables
			self.attrStore = Table.defaultAttributeStore
		else:
			self.attrStore = attrStore
		if not filename is None:
			self.load(filename)
		if not name is None:
			self.name = name

	def load(self, filename):
		"""
		Load data from either XML or TSV file
		"""
		with open(filename, 'r') as f:
			_,ext = os.path.splitext(filename);
			if ext=='.xml':
				# Parse the XML file
				dom = parse(f)
				f.close()
				self.name = dom.documentElement.tagName
				xmlrows = dom.getElementsByTagName('row')
				for xmlrow in xmlrows:
					attr = xmlrow.attributes
					for i in range(attr.length):
						name = attr.item(i).name
						if not name in self.attrs():
							# Add column to the table
							elt = Value(attr.item(i).value)
							index = self.attrStore.addAttr(name,elt.getType())
							self.columns.append(index)
							for r in self.data:
								r.append(Value())
					row = [unicode(xmlrow.getAttribute(name)) for name in self.attrs()]
					self.addrow(row)
			else:
				# Assume the input is a TSV file
				data = csv.reader(f,delimiter='\t')
				if len(data):
					for i in range(len(data[0])):
						self.attrStore('<untitled>'+str(i),None)
				for row in data:
					self.addrow([cell.decode('unicode-escape') for cell in row])

	def newTable(self):
		table = Table(name=self.name)
		# The new table shares the same attribute store, but attributes are duplicated
		table.attrStore = self.attrStore
		newAttrs = []
		for attr in self.columns:
			index = self.attrStore.addAttr(self.attrStore.getAttr(attr),self.getType(attr))
			newAttrs.append(index)
		table.columns = newAttrs
		return table
		
	def copy(self):
		table = self.newTable()
		table.data = [row[:] for row in self.data]
		idxmap = dict(zip(self.columns,table.columns))
		return table,idxmap
	def addrow(self, strrow):
		assert len(strrow) == len(self.columns)
		row = []
		for i in range(len(strrow)):
			val = Value(strrow[i])
			#print str(val.getType())+' et '+str(self.types[i])
			if self.getType(i) is type(None):
				# Initialize type
				self.setType(i,val.getType())
				row.append(val)
			elif val.getType() == self.getType(i) or val.getType() is type(None):
				row.append(val)
			else:
				row.append(Value(val=strrow[i]))
				if self.getType(i) != unicode:
					# Convert all other values in the column back to string
					# TODO : handle more fine-grained fallback (eg Float to Int)
					for r in self.data:
						if not r[i].getType() is type(None):
							r[i] = Value(val=unicode(r[i]))
					self.setType(i,unicode)
		self.data.append(row)

	def write(self, filename):
		"""
		Write the data to a TSV file
		"""
		f = open(filename,'wb')
		wr = csv.writer(f,delimiter='\t',quoting=csv.QUOTE_ALL)
		for row in self.data:
			strrow = []
			for cell in row:
				strrow.append(unicode(cell).encode('unicode-escape'))
			wr.writerow(strrow)
		f.close()

	def dump(self,n=-1,reset=False):
		"""
		Dumps n rows of the table to console.
		If reset=True, the dump starts over from the 1st row
		"""
		if n == -1:
			n = self.numRows()
		if reset:
			self.dumpcnt = 0
		colwidth = 17
		join = lambda l: '| '+' | '.join(l)+' |'
		dump = join([string.center(name[:colwidth],colwidth) for name in self.attrs()])
		sep = '+'*len(dump)
		dump = sep+'\n'+dump+'\n'+sep
		for i in [x+self.dumpcnt for x in range(n)]:
			if i >= len(self.data):
				break
			dump += '\n'+join([string.ljust(str(val)[:colwidth],colwidth) for val in self.data[i]])
			self.dumpcnt += 1
		dump += '\n'+sep
		print dump

	def attrs(self):
		for idx in self.columns:
			yield self.attrStore.getAttr(idx)
	def types(self):
		for idx in self.columns:
			yield self.attrStore.getType(idx)
	def name(self):
		return self.name
	def getAttr(self,idx):
		return self.attrStore.getAttr(idx)
	def getType(self,idx):
		return self.attrStore.getType(idx)
	def getAllIdxForAttr(self,attr):
		return [idx for idx,name in zip(self.columns,self.attrs()) if name == attr]
	def getIndex(self,attr):
		attrlist, = util.makelist(attr)
		result = []
		for a in attrlist:
			indexes = self.getAllIdxForAttr(a)
			if len(indexes) > 1:
				raise TableStructureError('Ambiguous attribute name')
			elif len(indexes) <= 0:
				raise TableAttrNotFoundError('Attribute not found in table')
			result.append(indexes[0])
		if isinstance(attr,basestring):
			return result[0]
		return result
	def getPos(self,index):
		# TODO: raise error if index not found
		indexlist, = util.makelist(index)
		positions = [-1]*len(indexlist)
		for i,idx1 in enumerate(indexlist):
			for pos,idx2 in enumerate(self.columns):
				if idx1 == idx2:
					positions[i] = pos
		if isinstance(index,(list,tuple)):
			return positions
		else:
			return positions[0]
	def hasAttr(self,attr):
		try:
			idx = self.getIndex(attr)
		except TableAttrNotFoundError:
			return False
		return True
	def addAttr(self,attr,ty=type(None),val=Value(None)):
		if val.getType() != type(None):
			ty = val.getType()
		index = self.attrStore.addAttr(attr,ty)
		self.columns.append(index)
		for row in self.data:
			row.append(val)
		return index

	def setAttrName(self,oldname,newname):
		idx = self.getIndex(oldname)
		self.attrStore.setName(idx,newname)
	def setNames(self,names):
		assert len(self.columns) == len(names)
		for idx,name in zip(self.columns,names):
			self.attrStore.setName(idx,name)
	def setType(self,idx,ty):
		self.attrStore.setType(idx,ty)

	def getRow(self, i):
		return self.data[i]
	def getColumnByPos(self, j):
		return [row[j] for row in self.data]
	def getColumn(self,idx):
		return self.getColumnByPos(self.columns.index(idx))
	def getColumnByAttr(self, attr):
		return self.getColumn(self.getIndex(attr))

	def numRows(self):
		return len(self.data)
	def numColumns(self):
		return len(self.columns)

	def select(self, condition, projIdx=None):
		if projIdx == None:
			projIdx = self.columns
		condition,projIdx = util.makelist(condition,projIdx)
		for c in condition:
			c.configureForTable(self)
		table = self.newTable()
		f = lambda row: reduce(__and__,[c.eval(row) for c in condition],True)
		table.data = [row[:] for row in (filter(f,self.data))]
		newProjIdx = [newIdx for oldIdx,newIdx in zip(self.columns,table.columns) if oldIdx in projIdx]
		tfinal,_ = table.project(newProjIdx)
		idxmap = dict(zip(projIdx,tfinal.columns))
		return tfinal,idxmap

	def project(self, attrIdx):
		# Duplicate columns are removed
		attrIdx = list(set(attrIdx))
		positions = self.getPos(attrIdx)
		table = Table(name=self.name)
		for idx in attrIdx:
			table.addAttr(self.getAttr(idx),self.getType(idx))
		for row in self.data:
			table.data.append([row[i] for i in positions])
		idxmap = dict(zip(attrIdx,table.columns))
		return table,idxmap

	def group(self, attrIdx, count=False, aggrAttrIdx=[], aggrFunc=[]):
		#TODO: remove attributes of intermediary tables in attribute store
		attrIdx,aggrAttrIdx,aggrFunc = util.makelist(attrIdx,aggrAttrIdx,aggrFunc)
		assert len(aggrAttrIdx) == len(aggrFunc)
		tmptable,idxmap = self.copy()
		aggrAttrIdx = util.mapIdx(aggrAttrIdx,idxmap)
		if count:
			cntIdx = tmptable.addAttr(gsql.WEIGHT_ATTR_NAME,val=Value(val=1))
			aggrAttrIdx.append(cntIdx)
			aggrFunc.append('cnt')
		# Find values for aggregation
		agg = aggregator.Aggregator(aggrFunc)
		aggCols = [tmptable.getColumn(idx) for idx in aggrAttrIdx]
		# Find groups of rows, and corresponding list of aggregation attributes
		tproj,_ = tmptable.project(attrIdx)
		groups = {}
		for i,row in enumerate(tproj.data):
			key = tuple(row)
			if not key in groups:
				groups[key] = []
			groups[key].append([col[i] for col in aggCols])
			# groups[key] is a list of lists: each inner list is the list of
			# aggregation values corresponding to this row
		# Create final table
		tfinal,_ = tmptable.project(attrIdx+aggrAttrIdx)
		for key in groups:
			aggvals = agg.calc(groups[key])
			newrow = list(key) + aggvals
			tfinal.data.append(newrow)
		idxmap = dict(zip(attrIdx+aggrAttrIdx,tfinal.columns))
		return tfinal,idxmap

	def join(self, table, joinconditions):
		joinIdx1 = [idx for idx,_ in joinconditions]
		joinIdx2 = [idx for _,idx in joinconditions]
		addIdx1 = [idx for idx in self.columns if not idx in joinIdx1]
		addIdx2 = [idx for idx in table.columns if not idx in joinIdx2]
		t = self.newTable()
		for attr in addIdx2:
			t.addAttr(attr,table.getType(attr))
		joinPos1 = self.getPos(joinIdx1)
		joinPos2 = table.getPos(joinIdx2)
		addPos1 = self.getPos(addIdx1)
		addPos2 = table.getPos(addIdx2)
		for row1 in self.data:
			for row2 in table.data:
				elmts1 = [row1[i] for i in joinPos1]
				elmts2 = [row2[i] for i in joinPos2]
				if elmts1 == elmts2:
					row = elmts1 + [row1[i] for i in addPos1] + [row2[i] for i in addPos2]
					t.data.append(row)
		idxmap = dict(zip(joinIdx1+addIdx1+addIdx2,t.columns)+zip(joinIdx2,t.columns[:len(joinIdx2)]))
		return t,idxmap

###################### CODE BELOW HAS NOT BEEN REWRITTEN YET ############################

	def rename(self, oldattr, newattr, copy=False):
		t = self.copy() if copy else self
		oldIdx = self.colIndex(oldattr)
		if isinstance(oldattr,basestring):
			# Rename one attribute
			t.columns[oldIdx] = newattr
		else:
			# Rename list of attributes
			for idx,new in zip(oldIdx,newattr):
				t.columns[idx] = new
		return t

	def order(self,attrlist,attrsort):
		if not isinstance(attrlist,list):
			attrlist = [attrlist]
		t = self.newTable()
		index = [self.columns.index(attr) for attr in attrlist+[attrsort]]
		for row in self.data:
			newrow = row[:]
			tuples = zip(*[newrow[idx].val for idx in index])
			tuples.sort(key=lambda tuple:tuple[-1])
			sortedattr = zip(*tuples)
			for i in range(len(index)):
				newrow[index[i]] = Value(val=tuple(sortedattr[i]))
			t.data.append(newrow)
		return t

	def expand(self,attrlist=None):
		if attrlist is None:
			# Expand all columns where values are lists or tuples
			if len(self.data):
				attrlist = []
				for val,attr in zip(self.data[0],self.columns):
					if isinstance(val.val,(list,tuple)):
						attrlist.append(attr)
		if not isinstance(attrlist,list):
			attrlist = [attrlist]
		t = Table(name=self.name)
		for index,attr in enumerate(self.columns):
			if not attr in attrlist:
				t.columns.append(attr)
				t.types.append(self.types[index])
		index = [self.columns.index(attr) for attr in attrlist]
		for row in self.data:
			tuples = zip(*[row[idx].val for idx in index])
			for i in range(len(tuples)-1):
				t1 = tuples[i]
				t2 = tuples[i+1]
				newrow = []
				for idx,val in enumerate(row):
					if not self.columns[idx] in attrlist:
						newrow.append(val)
				newrow += list(t1+t2)
				t.data.append(newrow)
		for idx,attr in zip(index,attrlist):
			t.columns.append(attr+'1')
			t.types.append(self.types[idx])
		for idx,attr in zip(index,attrlist):
			t.columns.append(attr+'2')
			t.types.append(self.types[idx])
		return t

	def colIndex(self, attribute):
		if isinstance(attribute,basestring):
			return self.columns.index(attribute)
		else:
			return tuple(self.columns.index(att) for att in attribute)

	def getTypes(self, attributes):
		return list(self.types[i] for i in self.colIndex(attributes))

	def getElmtsAtIdx(self, row, indexes):
		return [row[i] for i in indexes]

	def getElmts(self, row, attributes):
		indexes = self.colIndex(attributes)
		return self.getElmtsAtIdx(row, indexes)

	def getAttrDict(self, row, attributes):
		attrIdx = self.colIndex(attributes)
		attrDict = {}
		for attr,idx in zip(attributes,attrIdx):
			attrDict[attr] = row[idx]
		return attrDict