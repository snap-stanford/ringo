Part 1:
=======
Pre-process the input datasets to look like the input we present in the VLDB paper
and website use case - i.e. a single posts table with the schema: 
posts(Id, PostTypeId, AcceptedAnswerId, OwnerUserId, Body, Tag)

Note: There could be many entrance for the same post but with different tags, as each post
can have an arbitrary number of tags.

Input:
====== 
/dfs/ilfs2/0/ringo/StackOverflow_VLDB/posts.xml
An XML dump of all posts from StackOverflow (not including tags)

/dfs/ilfs2/0/ringo/StackOverflow_VLDB/tags.tsv
A TSV file containing the following relation: (Id, Tag)
This file has an entry for every tag of a post. 
Only question posts (no answers) appear in this file.

Note: There is also an XML file for a raw dump of the tags under /dfs/ilfs2/0/ringo/StackOverflow.old/
with an entry for each question post + all the tags associated with that post.

Scripts:
=======
parseStackOverflowXml.py (taken from Martin and slightly modified):
	Parses the xml file to a tsv file. I replace all text field values with a constant 
	string "a". Feel free to modify it if you want to keep string values / map them to 
	integers.. In the script you can define a list of size parameters. 
	For every such parameter Sz, the script would generate a TSV file generated from the 
	first Sz post records ("posts_<Sz>.test.tsv").
	The entire dataset consists of 15,838,934 post records.
	
processPosts.py:
	Takes the output of parseStackOverflowXml.py and projects it to the following schema:
	posts(Id, PostTypeId, AcceptedAnswerId, OwnerUserId, Body)
	Use: python processPosts.py input output 
	- e.g. python processPosts.py posts_1000.test.tsv posts_1000.tsv

joinPostsTags.py: 
	Takes a the output of processPosts.py (i.e. all posts - without tags) and tags.tsv 
	(question ids + tags) and produces a file 'so_posts.tsv' with all posts (see note) 
	including tags - i.e. posts(Id, PostTypeId, AcceptedAnswerId, OwnerUserId, Body, Tag)
	Use: python joinPostsTags.py posts_input tags_input 
	- e.g. python joinPostsTags.py posts_1000.tsv tags.tsv
	
	Note: 'so_posts.tsv' will contain all question posts and all accepted answers posts, 
	with a record (row) for each tag of each such post. Posts which are answers
	that were not accepted are lost.
	
Part 2:
========
The use case as appears in the VLDB paper, and in more detail on the website:
Load posts table
Project to relevant schema
Select 'java' posts
Select questions and select answers
Join questions and accepted answers
Create user network
Run PageRank
Transform PageRank output to a table object
Order the table by score
Save table to output file

Use: python usecase so_posts.tsv
	
