***********************************************************************************
* Use case #6: (Paper) get top Python experts from the StackOverflow dataset      *
***********************************************************************************

Dataset: StackOverflow
Input directory: /dfs/ilfs2/0/ringo/StackOverflow/

Usage: python 02-DBLP-snap.py source destination
       python 02-DBLP-ringo.py source destination

  * Arguments:

  posts.tsv: path to posts.tsv file
  tags.tsv: path to tags.tsv file
  dest.tsv: output .tsv file containing expert scores. It stores the list of Python experts, sorted in descending order. For each user, the Authority score, the score for comments and the overall final score are given

  * Output: the top 20 Python experts ordered by decreasing authority score

        $python 06-Paper-simple-snap.py /dfs/ilfs2/0/ringo/StackOverflow/posts.tsv /dfs/ilfs2/0/ringo/StackOverflow/tags.tsv output

        [load posts]    Elapsed: 4.69 seconds, Rows: 15838934
        [load tags] Elapsed: 15.61 seconds, Rows: 16413230
        [select]    Elapsed: 3.91 seconds, Rows: 214856
        [join]  Elapsed: 1.79 seconds, Rows: 214856
        [join]  Elapsed: 1.62 seconds, Rows: 141816
        [authority score]   Elapsed: 0.87 seconds, Rows: 59343
        [order] Elapsed: 11.11 seconds, Rows: 59343
        [save]  Elapsed: 0.05 seconds, Rows: 59343
        UserId                   Authority                t5_id                    
        ---------------------------------------------------------------------------
        95810                    0.648853                 2339                     
        100297                   0.502589                 3131                     
        20862                    0.299495                 1025                     
        190597                   0.234737                 4707                     
        279627                   0.116245                 12593                    
        12030                    0.092530                 349                      
        104349                   0.090890                 2526                     
        174728                   0.081994                 4484                     
        748858                   0.081174                 29763                    
        14343                    0.076366                 812                      
        7432                     0.071561                 380                      
        10661                    0.067616                 226                      
        61974                    0.066820                 5402                     
        846892                   0.065333                 27319                    
        908494                   0.065223                 33350                    
        4279                     0.059675                 183                      
        367273                   0.051277                 13309                    
        505154                   0.045726                 13288                    
        148870                   0.044857                 3649                     
        17160                    0.044783                 346                      

        $ ls output
        experts.tsv
