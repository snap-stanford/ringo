***************************************************************************
* Use case #2: create a coauthorship network and get the table of authors * 
*              sorted by PageRank score                                   *
***************************************************************************

Dataset: DBLP
Input file: /dfs/ilfs2/0/ringo/DBLP/authors.tsv

Usage: python 02-DBLP-snap.py source destination
       python 02-DBLP-ringo.py source destination

  * Arguments:

  source: input file
  destination: directory containing the output files.
    The only output file is table.tsv. It stores the list of PageRank scores of authors, sorted in descending order.

  * Output: the top 20 authors ordered by PageRank score
    Example:

        Name                          PageRank
        -----------------------------------------
        Jos                           0.00222
        J                             0.00178
        G                             0.00091
        Andr                          0.00090
        Fran                          0.00073
        S                             0.00064
        Fr                            0.00056
        Jo                            0.00049
        St                            0.00047
        Mar                           0.00045
        C                             0.00044
        Jes                           0.00038
        R                             0.00037
        H                             0.00035
        Bj                            0.00033
        M                             0.00032
        V                             0.00031
        Ren                           0.00030
        Jean-Fran                     0.00024
        L                             0.00021