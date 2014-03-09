*************************************************************************************
* Use case #9: Find users who voted for similar candidates on Wikipedia admin 
* elections
************************************************************************************

Dataset: Wikipedia Vote
Input file: /dfs/ilfs2/0/ringo/Wikipeda/wiki-Vote.txt
Output file: output.tsv

Usage: python 09-Wikipedia-snap.py /dfs/ilfs2/0/ringo/Wikipedia/wiki-Vote.txt output.tsv

  * Arguments:

  wiki-Vote.txt: path to Wikipedia voting dataset
	output.tsv: path to the file where the result will be saved. 

  * Output: User-user pairs who voted for similar candidates (Jaccard distance <= 0.5)

  * Example:

        $ python 09-Wikipedia-snap.py /dfs/ilfs2/0/ringo/Wikipedia/wiki-Vote.txt output.tsv
				[load Votes]      Elapsed: 0.07 seconds, Rows: 103689
				[SimJoinPerGroup complete] Elapsed: 34.80 seconds, Rows: 27434
				[Select complete] Elapsed: 0.01 seconds, Rows: 21324

