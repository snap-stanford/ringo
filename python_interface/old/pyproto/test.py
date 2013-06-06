from table import Table
import gbuild

if 0:
    t = Table('data/posts.xml')
    t2 = t.group(['OwnerUserId'],['AnswerCount','Score'],'list')
    t3 = t2.sort('AnswerCount','Score')
    t4 = t3.expand()

g = gbuild.CG4(10)