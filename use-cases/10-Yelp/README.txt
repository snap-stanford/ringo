*************************************************************************************
* Use case #10: Find businesses that are within 2 kilometers of each other
************************************************************************************

Dataset: Yelp Academic Dataset
Input file: /dfs/ilfs2/0/ringo/Yelp/yelp.txt
Output file: output.tsv

Usage: python 10-Yelp-snap.py /dfs/ilfs2/0/ringo/Wikipedia/yelp.txt output.tsv

  * Arguments:

  yelp.txt: path to Wikipedia voting dataset
	output.tsv: path to the file where the result will be saved. 

  * Output: Businesses that are close to each other (Haversine distance <= 2 km)

  * Example:

        $ python 10-Yelp-snap.py /dfs/ilfs2/0/ringo/Wikipedia/yelp.txt output.tsv
				[load Yelp]       Elapsed: 0.02 seconds, Rows: 4999
				[SimJoin complete]Elapsed: 36.00 seconds, Rows: 711921
				[Project complete]Elapsed: 0.02 seconds

