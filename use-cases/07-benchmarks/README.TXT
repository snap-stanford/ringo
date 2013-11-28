Benchmarks
Nov 25, 2013

grtxt2bin.py <srcfile> <dstfile>
	reads a source input file in the text format and produces a
	destination output file in the SNAP binary format. The input
	file is an edge list, specifying a directed graph. The output
	file contains a SNAP PNGraph.

grpagerank.py <srcfile>
	reads a source input file which contains a PNGraph in the
	SNAP binary format and calculates a pagerank.

01-tbtxt2bin.py <srcfile> <dstfile>
	reads a source input file in the text format and produces a
	destination output file in the SNAP binary format. The input
	file is two integer columns. The output file contains a SNAP
	TTable.

02-tbbin2gr2tb.py <srcfile>
	reads a table from a source input file in binary format, builds
	a graph from this table and extracts a table from the resulting
	graph. The table contains two integer columns that represent 
	the edges of the graph. The final table contains three integer
	columns representing the list of edges in the graph (edge id, 
	source id, destination id)

03-tbselltnewtb.py
	reads a table from a source input file in binary format, and
	creates a new table with the same schema as the first table
	but containing only the rows where the first value is < 10000.

04-tbselgtnewtb.py
	reads a table from a source input file in binary format, and
	creates a new table with the same schema as the first table
	but containing only the rows where the first value is > 10000.