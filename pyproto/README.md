SNAPGraphConstruction
=====================

Idea: Provide a language and interface to convert raw data into meaningful graphs

Motivation: Most of the research in network analysis is based on pre-labeled graphs.
However, there may be many other ways of defining nodes and edges. Each definition could
potentially reveal important properties of the network.

Plan of Action:
1.  Define the language to do relational algebra queries on data.
2.  Write functions that help the user select parts of data that could be labeled nodes
    and edges and add to a graph

Assumptions:
1.  Data set includes schema of data
2.	Data comes in as .xml files 
3.	Data is of three basic types: float, string and dates

Issues:
1. 	TSV format not well defined, encode escape working with python
2.	Memory management
3.	Indexes? performance matters

-------------
Attempt 1:
-------------

# User interface

ringo = new Ringo()
node1 = NodeDescription(file, condition)
node2 = NodeDescription(file, condition)
edges = EdgeDescription([JoinCondition])
graph = ringo.createGraph(node1, node2, edges)

# createGraph implementation
ringo.createGraph (node1, node2, edges)
	file1 = node1.file
	file2 = node2.file
	attrs1 = []
	attrs2 = []
	attrs1.append(node1.condition.attr)
	if (file1 == file2):
		attrs1.append(node2.condition.attr)
		for cond in edges.conditions:
			attr1.append(cond.attr1)
			attrs1.append(cond.attr2)

		table = Table(file1, attrs1)
		table2 = select(table, node1.condition)
		table3 = select(table, node2.condition)
		table4 = join(table2, table3, edges.conditions)
		nodes = addNodes(table4, node1.condition.attr, node2.condition.attr)
		addEdges(table4, nodes)
	else
		attrs2.append(node2.condition.attr)
		for cond in edges.conditions:
			if cond.file == file1 and cond.file2 is None:
				attrs1.append(cond.attr1)
				attrs1.append(cond.attr2)
			elif cond.file == file1 and cond.file2 is not None:
				attrs1.append(cond.attr1)
				attrs2.append(cond.attr2)
			else
				attrs2.append(cond.attr1)
				attrs2.append(cond.attr2)
			
		table = Table(file1, attrs1)
		table2 = Table(file2, attrs2)
		table3 = select(table, node1.condition)
		table4 = select(table2, node2.condition)
		table5 = join(table3, table4, edges.conditions)
		nodes = addNodes(table5, node1.condition.attr, node2.condition.attr)
		addEdges(table5, nodes)

-------------------
Attempt 2:
-------------------

# Notes on Latest model implementation

What the user calls:
	ringo = ringo.Ringo(files)
	graph = ringo.makegraph(starttable, nodedesc, edgedesc, nodeAttrs, edgeAttrs, addNodeAttrs, type)

want something like

	graph = ringo.makegraph(starttable,  graphdesc, src, dst, nodeattrs, edgeattrs)

Ringo: Class
	tables		# all data
	wtable		# working table built along the way by applying nodedesc and edgedesc
	wcol		# working column
	srctable	# state of working table after applying nodedesc
	graph

Ringo API:

	select(expression)
	label(newlabel)
	join(newtable, column)
	group(groupColumn, groupByColumns)
	order(orderByColumns) # right now we have order(orderClumnnName, orderByColumns)
	number, count and next
	unique(columnName) # right now we have unique() which runs unique based on working column
	changeWorkingColumn(columnName)

Expressions for select and join
	selection: expression involves boolean conjunction and/or disjunction of conditions
			 	condition: columnName operator value
	join: implicit equijoin
			We could make it a boolean conjunction and/or disjunction of join conditions
				joinCondition: columnName1 operator columnName2


