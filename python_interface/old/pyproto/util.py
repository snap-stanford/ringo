def makelist(*args):
    return ([obj] if not isinstance(obj,(list,tuple)) else obj for obj in args)

def mapIdx(srcIdx,*args):
    srcIdxList, = makelist(srcIdx)
    destIdx = []
    for idx in srcIdxList:
        index = idx
        for idxmap in args:
            index = idxmap[index]
        destIdx.append(index)
    if isinstance(srcIdx,(list,tuple)):
        return destIdx
    else:
        return destIdx[0]

def mergeIdxmap(*args):
    finalmap = {}
    init = True
    for idxmap in args:
        if init:
            finalmap = idxmap
            init = False
        for src,dest in finalmap.iteritems():
            if dest in idxmap:
                finalmap[src] = idxmap[dest]
    return finalmap