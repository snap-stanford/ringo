"""
 Script to parse the iPlane dataset and output the data in TSV format
 The iPlane dataset can be found at http://iplane.cs.washington.edu/data/data.html
"""

import sys

TRACEROUTE_FILE_NAME = "traceroutes.tsv"
COUNTRIES_FILE_NAME = "countries.tsv"

if len(sys.argv) < 4:
  print """Usage: python parse.py sourcedir destdir geoipdir
  sourcedir: input directory containing RIPE traceroutes in text format
  destdir: output directory
  geoipdir: directory containing GeoIP.dat and geoip.py

  Example: python parse.py /dfs/ilfs2/0/ringo/RIPE/unpacked /dfs/ilfs2/0/ringo/RIPE/data /dfs/ilfs2/0/ringo/RIPE/GeoIP"""
  exit(1)

geoIPDir = sys.argv[3]
sys.path.append(geoIPDir)
import os
import geoip
tracerouteId = 0

def parseFile(fileName, tracerouteFile, countryDict, G):
  global tracerouteId
  try:
    with open(fileName) as source:
      print 'Parsing file %s...' % fileName
      for line in source:
        hop, rest = line.split(": ",1)
        if hop == 'destination':
          tracerouteId += 1
          continue
        ip, latency, ttl = rest.split()
        tracerouteFile.write("\t".join([str(tracerouteId), hop,ip,latency,ttl]) + "\n")
        try:
          countryDict[ip] = G.country(ip)
        except IndexError:
          countryDict[ip] = ''
          print 'Invalid country for ip %s' % ip
  except ValueError:
    print 'File %s is invalid' % fileName

srcDir = sys.argv[1]
dstDir = sys.argv[2]
try:
  os.makedirs(dstDir)
except OSError:
  pass
dataFiles = [os.path.join(srcDir, f) for f in os.listdir(srcDir) if os.path.isfile(os.path.join(srcDir,f))]
tracerouteFilename = os.path.join(dstDir, TRACEROUTE_FILE_NAME)
countryFilename = os.path.join(dstDir, COUNTRIES_FILE_NAME)
countryDict = {}
G = geoip.GeoIP(os.path.join(geoIPDir, 'GeoIP.dat'))
with open(tracerouteFilename, "w") as tracerouteFile:
  for fileName in dataFiles:
    parseFile(fileName, tracerouteFile, countryDict, G)
with open(countryFilename, "w") as countryFile:
  for ip, country in countryDict.iteritems():
    countryFile.write(ip + "\t" + country + "\n")
