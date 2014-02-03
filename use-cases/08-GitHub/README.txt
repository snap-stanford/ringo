***************************************************************************
* Use case #8: Link Prediction for collaboration on Github. Create a 	  *
		collaboration graph from GitHub Archival data, randomly   *
		select nodes, make predictions using random walk with  	  *
		restarts and evaluate from the the delta graph. 	  *
***************************************************************************

Dataset: GitHub
Input dir: /dfs/ilfs2/0/ringo/GitHub/06-15-2012_11-16-2012

Usage: python 08-GitHub-snap.py <authors.tsv> <delta_date>

  * Arguments:
	  authors.tsv: path to authors.tsv file
	  year.tsv: path to year.tsv file
	  outputdir: output directory
	    The only output file is table.tsv. It stores the list of PageRank scores of authors, sorted in descending order.

  * Output: 20 iterations of random walk with restarts for randomly selected nodes and corresponding Precision and Average Index

  * Example (scores are normalized so that the top score is 1):

        $ python 02-DBLP-snap.py /dfs/ilfs2/0/ringo/DBLP/authors.tsv /dfs/ilfs2/0/ringo/year.tsv output

        [load authors table]  Elapsed: 6.34 seconds
        [load year table] Elapsed: 1.25 seconds
        [select]  Elapsed: 0.01 seconds
        [join]  Elapsed: 2.55 seconds
        [join]  Elapsed: 80.61 seconds
        [select]  Elapsed: 70.03 seconds
        [graph] Elapsed: 80.38 seconds
        [page rank] Elapsed: 440.39 seconds
        [order] Elapsed: 158.91 seconds
        [division]  Elapsed: 0.02 seconds
        [save]  Elapsed: 1.33 seconds
        Author                   PageRank                 
        --------------------------------------------------
        Gerrit Bleumer           1.000000                 
        Alex Biryukov            0.923510                 
        Christian S. Jensen      0.629050                 
        Carlisle Adams           0.592544                 
        Friedrich L. Bauer       0.577657                 
        Burton S. Kaliski Jr.    0.576965                 
        Burt Kaliski             0.566139                 
        Bart Preneel             0.556824                 
        Richard T. Snodgrass     0.552596                 
        Christodoulos A. Floudas 0.484053                 
        Anne Canteaut            0.438291                 
        Christophe De Cannire    0.375770                 
        Peter Landrock           0.375583                 
        Yvo Desmedt              0.364126                 
        Berry Schoenmakers       0.336231                 
        Alfred Menezes           0.323041                 
        Darrel Hankerson         0.321223                 
        Caroline Fontaine        0.319959                 
        Dan Boneh                0.312743                 
        Tor Helleseth            0.286676                 

        $ ls output
        table.tsv
