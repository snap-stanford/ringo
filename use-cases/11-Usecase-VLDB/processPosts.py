import sys

srcfile = sys.argv[1]
dstfile = sys.argv[2]
keep_schema = False
with open(srcfile,"r") as src: 
  with open(dstfile, "wb") as dst:
    wantedAttrNames = ["Id", "PostTypeId", "AcceptedAnswerId", "OwnerUserId", "Body"]
    wantedAttrCols = {"Id":16, "PostTypeId":11, "AcceptedAnswerId":9, "OwnerUserId":12, "Body":0}
    attrNum = len(wantedAttrNames)
    count = 0
    for line in src:
      if count == 0:
        if keep_schema:
        	for i in range(0,attrNum-1):
          		dst.write(wantedAttrNames[i] + '\t')
        	dst.write(wantedAttrNames[attrNum-1] + '\n')
      else:
        attrs = line.split('\t')
        for i in range(0,attrNum-1):
          dst.write(attrs[wantedAttrCols[wantedAttrNames[i]]] + '\t')
        dst.write(attrs[wantedAttrCols[wantedAttrNames[attrNum-1]]] + '\n')
      count = count+1
    
	
  