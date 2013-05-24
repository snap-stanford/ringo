import numpy as np
import pandas as pd

folder = '../../data_full/'

def QAGraph():
    posts = pd.read_csv(folder+'comments.tsv',sep='\t')
    posts1 = posts[posts['PostTypeId'] == 2]
    #rename columns
    merge(posts1,posts,on='')
    posts
    posts2 = posts[posts['PostTypeId'] == 1]