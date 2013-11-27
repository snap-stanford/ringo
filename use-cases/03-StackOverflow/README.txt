***************************************************************************
* Use case #3: get top Python experts from the StackOverflow dataset      *
***************************************************************************

Dataset: StackOverflow
Input directory: /dfs/ilfs2/0/ringo/StackOverflow.old/

Usage: python 02-DBLP-snap.py source destination
       python 02-DBLP-ringo.py source destination

  * Arguments:

  source: input directory containing posts.tsv and comments.tsv files
  destination: directory containing the output files.
    The only output file is table.tsv. It stores the list of Python experts, 
    sorted in descending order. For each user, the Authority score, the score for 
    comments and the overall final score are given

  * Output: the top 20 Python experts ordered by decreasing authority score

        $python 03-StackOverflow-snap.py /dfs/ilfs2/0/ringo/StackOverflow.old/ output

        [load posts]  Elapsed: 13.67 seconds, Rows: 10338371
        [copy & project]  Elapsed: 1.09 seconds, Rows: 10338371
        [rename]  Elapsed: 0.00 seconds, Rows: 10338371
        [select]  Elapsed: 2.81 seconds, Rows: 125892
        [project] Elapsed: 0.02 seconds, Rows: 10338371
        [rename]  Elapsed: 0.00 seconds, Rows: 10338371
        [join]  Elapsed: 1.04 seconds, Rows: 279820
        [graph] Elapsed: 0.19 seconds, Nodes: 68686, Edges: 279820
        [authority score] Elapsed: 1.53 seconds, Rows: 68686
        [load]  Elapsed: 3.33 seconds, Rows: 13252467
        [union] Elapsed: 0.64 seconds, Rows: 559640
        [unique]  Elapsed: 0.57 seconds, Rows: 399511
        [join]  Elapsed: 1.66 seconds, Rows: 539937
        [count] Elapsed: 0.33 seconds, Rows: 48142
        [division]  Elapsed: 0.01 seconds, Rows: 48142
        [project] Elapsed: 0.02 seconds, Rows: 48142
        [join]  Elapsed: 0.05 seconds, Rows: 43680
        [division]  Elapsed: 0.00 seconds, Rows: 43680
        [order] Elapsed: 23.66 seconds, Rows: 43680
        [save]  Elapsed: 0.03 seconds, Rows: 43680
        Expert                   FinalScore               
        --------------------------------------------------
        10661                    0.067785                 
        0                        0.044791                 
        95810                    0.026765                 
        20862                    0.010199                 
        84270                    0.004810                 
        4279                     0.004523                 
        12855                    0.004129                 
        126214                   0.003788                 
        174728                   0.003740                 
        17160                    0.002559                 
        279627                   0.001867                 
        190597                   0.001343                 
        14343                    0.001333                 
        104349                   0.001239                 
        893                      0.001161                 
        6946                     0.001108                 
        12030                    0.001101                 
        8206                     0.000880                 
        136829                   0.000876                 
        6899                     0.000872                 

        $ ls output
        table.tsv
