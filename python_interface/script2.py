import ringo as rg

rg = rg.Ringo("PYTHON")
rg.load("data/posts.tsv")
rg.start("posts","OwnerUserId")
#rg.dump()
print rg.getSize()
rg.select(">=","Tags","10000")
#rg.dump()
print rg.getSize()
rg.link("OwnerUserId")
rg.join("posts","OwnerUserId")
#rg.dump()
print rg.getSize()
