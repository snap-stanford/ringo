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

What's done:
1. Basic class definitions for
	- table
	- graph
	- node
	- edge
	- condition
	- value
2.	Basic get functions for class fields
3.	graphconstruction.py has basic relational algebra primitives defined and 
	some of them are implemented


