import ringo
import time
import sys

#folder = '/lfs/local/0/ringo/testfiles/'
folder = 'testfiles/'
ITERATIONS = 10

class Timer:
  def __init__(self):
    self.cumul = 0
    self.start = time.time()
  def gettime(self):
    duration = time.time()-self.start
    self.start = time.time()
    self.cumul += duration
    return duration
  def showtime(self,op):
    print op + ":\t" + "{0:.3f}".format(self.gettime())
  def showresults(self,op,df):
    print op + ":\t" + "{0:.3f}".format(self.gettime()) + " (working table has " + str(len(df)) + " rows)"
  def updatetime(self,op,store):
    store.update(op,self.gettime())

class OpTimes:
  def __init__(self,length):
    self.tottimes = {}
    self.operations = []
    self.length = length
  def update(self,op,time):
    if not op in self.tottimes:
      self.tottimes[op] = 0
      self.operations.append(op)
    self.tottimes[op] += time
  def gettime(self,op):
    return self.tottimes[op]/self.length
  def printResults(self):
    for op in self.operations:
      print op + ": " + "{0:.3f}".format(self.gettime(op)) + " seconds"

def QAGraph(s, qa_times):
  timer = Timer()
  # Load
  rg = ringo.Ringo()
  rg.load(folder + 'posts_' + str(s) + '.hashed.tsv','posts')
  rg.start('posts','OwnerUserId')
  timer.updatetime("Read", qa_times)
  total = Timer()
  # Select
  rg.label('UserId1')
  rg.select('PostTypeId == 2')
  timer.updatetime("Select", qa_times)
  # Join
  rg.link('ParentId')
  rg.join('posts','Id')
  timer.updatetime("Join", qa_times)
  # Group
  rg.link('OwnerUserId')
  rg.label('UserId2')
  rg.group('Group','UserId1','UserId2')
  rg.unique()
  timer.updatetime("Group", qa_times)
  total.updatetime("Total", qa_times)

def CommentsGraph(s, comm_times):
  timer = Timer()
  # Load
  rg = ringo.Ringo()
  rg.load(folder + 'comments_' + str(s) + '.hashed.tsv','comments')
  rg.start('comments','UserId')
  timer.updatetime("Read", comm_times)
  total = Timer()
  # Join
  rg.label('UserId1')
  rg.link('PostId')
  rg.join('comments','PostId')
  timer.updatetime("Join", comm_times)
  # Select
  rg.link('UserId')
  rg.label('UserId2')
  rg.select('UserId1 != UserId2')
  timer.updatetime("Select", comm_times)
  # Group
  rg.group('Group','UserId1','UserId2')
  rg.unique()
  timer.updatetime("Group", comm_times)
  total.updatetime("Total", comm_times)

def main():
  sizes = [10,30,100,300,1000,3000,10000]
  print "\nQ&A Graph:"
  for s in sizes:
    qa_times = OpTimes(len(sizes))
    sys.stdout.write(str(s*1000) + " rows")
    for i in xrange(ITERATIONS):
      sys.stdout.write('.')
      sys.stdout.flush()
      QAGraph(s, qa_times)
    print ""
    qa_times.printResults()
  print "\nCommon Comments Graph:"
  for s in sizes:
    comm_times = OpTimes(len(sizes))
    sys.stdout.write(str(s*1000) + " rows")
    for i in xrange(ITERATIONS):
      sys.stdout.write('.')
      sys.stdout.flush()
      CommentsGraph(s, comm_times)
    print ""
    comm_times.printResults()

if __name__ == "__main__":
  main()
