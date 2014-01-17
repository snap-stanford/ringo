*******************************************************************************
* Use case #1: create a coauthorship network and print its estimated diameter *
*******************************************************************************

Dataset: DBLP
Input file: /dfs/ilfs2/0/ringo/DBLP/authors.tsv

Usage: python 01-DBLP-snap.py <authors.tsv> <year.tsv> <outputdir>
       python 01-DBLP-ringo.py <authors.tsv> <year.tsv> <outputdir>

  * Arguments:

  authors.tsv: path to authors.tsv file
  year.tsv: path to year.tsv file
  outputdir: output directory (for saving the table of edges and the coauthorship network)
    The output files are:
    - graph: stores the coauthorship network (SNAP object)
    - table.tsv: stores the final Ringo table from which the coauthorship network is created

  * Output: the last line of the output is the estimated diameter of the DBLP coauthorship network

  * Example:

        $ python 01-DBLP-snap.py /dfs/ilfs2/0/ringo/DBLP/authors.tsv /dfs/ilfs2/0/ringo/DBLP/year.tsv output

        [load]  Elapsed: 6.59 seconds, Rows: 2734707
        [load year table] Elapsed: 1.26 seconds, Rows: 1039160
        [select]  Elapsed: 0.01 seconds, Rows: 654161
        [join]  Elapsed: 2.49 seconds, Rows: 1900913
        [join]  Elapsed: 84.48 seconds, Rows: 143130017
        [graph] Elapsed: 83.17 seconds, Nodes: 627535, Edges: 142920678
        [diameter (10 test nodes)]  Elapsed: 285.07 seconds
        Diameter: 7.89169

        $ ls output
        graph   table.tsv
