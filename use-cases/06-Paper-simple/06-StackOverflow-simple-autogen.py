import ringo

def generate(engine,filename0,filename1):
    t1=engine.LoadTableTSV([('PostId', 'int'), ('UserId', 'int'), ('AnswerId', 'int')],filename0)
    t2=engine.LoadTableTSV([('PostId', 'int'), ('Tag', 'string')],filename1)
    engine.Select(t2,'Tag = python',CompConstant=True)
    t3=engine.Join(t1,t2,'PostId','PostId')
    t4=engine.Join(t3,t1,'AnswerId','PostId')
    return t4

engine=ringo.Ringo()
