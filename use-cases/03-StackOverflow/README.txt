***************************************************************************
* Use case #2: get top Python experts from the StackOverflow dataset      *
***************************************************************************

Dataset: StackOverflow
Input directory: /dfs/ilfs2/0/ringo/StackOverflow/

Usage: python 02-DBLP-snap.py source destination
       python 02-DBLP-ringo.py source destination

  * Arguments:

  source: input directory
  destination: directory containing the output files.
    The only output file is table.tsv. It stores the list of Python experts, 
    sorted in descending order. For each user, the Authority score, the score for 
    comments and the overall final score are given

  * Output: the top < 20 authors ordered by PageRank score
    Example:

        Expert              CommentScore                 Authority            FinalScore    
        ---------------------------------------------------------------------------------
        147                 0.17647                       0.01134              0.00200                  
        111                 0.11765                       0.01124              0.00132                  
        153                 0.05882                       0.01528              0.00090                  
        161                 0.05882                       0.01528              0.00090                  
        154                 0.05882                       0.00222              0.00013                  
        61                  0.05882                       0.00116              0.00007                  