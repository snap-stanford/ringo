*******************************************************************************
* Use case #1: create a coauthorship network and print its estimated diameter *
*******************************************************************************

Dataset: DBLP
Input file: /dfs/ilfs2/0/ringo/DBLP/authors.tsv

Usage: python 01-DBLP-snap.py source destination
       python 01-DBLP-ringo.py source destination

  * Arguments:

  source: input file
  destination: directory containing the output files.
    The output files are:
    - table.tsv: stores the final Ringo table from which the coauthorship network is created
    - graph.tsv: stores the coauthorship network (SNAP object)

  * Output: the last line of the output is the estimated diameter of the DBLP coauthorship network
    Example: "Diameter: 6.81974"