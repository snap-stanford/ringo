import sys,os
ROOT_DIR = os.path.join(os.path.dirname(__file__),"..")
sys.path.append(ROOT_DIR)
import ringo

TEST_DIR = os.path.join(ROOT_DIR,"test")

engines = ["PANDAS","PYTHON"]
for eng in engines:
  print "Using engine " + eng
  rg = ringo.Ringo(eng)
  rg.load(os.path.join(TEST_DIR,"data","posts.tsv"))
  rg.start("posts","OwnerUserId")
  rg.label("UID1")
  rg.link("PostTypeId")
  rg.label("PT1")
  rg.link("ParentId")
  rg.join("posts","Id")
  rg.link("PostTypeId")
  rg.label("PT2")
  rg.link("OwnerUserId")
  rg.label("UID2")
  rg.select("&&","==","PT1","2","==","PT2","1")
  rg.unique("UID1","UID2")
  rg.build_graph()
