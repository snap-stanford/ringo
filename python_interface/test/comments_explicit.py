import sys,os
ROOT_DIR = os.path.join(os.path.dirname(__file__),"..")
sys.path.append(ROOT_DIR)
import ringo

TEST_DIR = os.path.join(ROOT_DIR,"test")

engines = ["PANDAS","PYTHON"]
for eng in engines:
  print "Using engine " + eng
  rg = ringo.Ringo(eng)
  rg.load(os.path.join(TEST_DIR,"data","comments.tsv"))
  rg.start("comments","UserId")
  rg.label("UID1")
  rg.link("PostId")
  rg.join("comments","PostId")
  rg.link("UserId")
  rg.label("UID2")
  rg.select("!=","UID1","UID2")
  rg.unique("UID1","UID2")
  rg.build_graph()
