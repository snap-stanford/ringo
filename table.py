
import csv
import os
from xml.dom.minidom import parse

class Table:

	def __init__(self, name):
		self.name = name
		self.attributes = []
		self.data = []

	def set_attributes(self, attributes):
		for attr in attributes:
			self.attributes.append(attr)

	def load(self, filename):
		"""
		Load data from either XML or TSV file
		"""
		f = open(filename, 'r')
		_,ext = os.path.splitext(filename);
		if ext=='.xml':
			# Parse the XML file
			dom = parse(f)
			f.close()
			xmlrows = dom.getElementsByTagName('row')
			first = True
			for xmlrow in xmlrows:
				a = xmlrow.attributes
				if first:
					# Create the list of attributes
					for i in range(a.length):
						self.attributes.append(a.item(i).name)
					first = False
				row = []
				for i in range(a.length):
					row.append(a.item(i).value)
				self.data.append(row)
		else:
			# Assume the input is a TSV file
			data = csv.reader(f,delimiter='\t')
			for row in data:
				self.data.append([cell.decode('unicode-escape') for cell in row])

	def write(self, filename):
		"""
		Write the data to a TSV file
		"""
		f = open(filename,'wb')
		wr = csv.writer(f,delimiter='\t')
		for row in self.data:
			wr.writerow([cell.encode('unicode-escape') for cell in row])
		f.close()

	def name(self):
		return self.name

	def ithrow(self, data, i):
		return data[i]

	def columnbyattr(self, data, attr):
		result = {}
		for row in data:
			result.add(row[attr])

		return result