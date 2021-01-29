import copy

def getN(d, count, nMin=99, resMin=99, keys=[0,0,0], maxDepth=0, best_keys=[]):
    maxDepth += 1
    for x in d.keys():
        keys[maxDepth-1] = x
        if type(d[x]) == type(0):
            if (d[x] < resMin) and (d[x]>=0):
                nMin = count + x
                resMin = d[x]
                if maxDepth < len(keys):
                    for i in range(maxDepth, len(keys)):
                        keys[i] = 0
                best_keys = copy.deepcopy(keys)
            elif (d[x] <= resMin) and ((count + x) < nMin):
                nMin = count + x
                resMin = d[x]
                if maxDepth < len(keys):
                    for i in range(maxDepth, len(keys)):
                        keys[i] = 0
        else:
            nMin, resMin, best_keys = getN(d[x], count+x, nMin=nMin, resMin=resMin, keys=keys, maxDepth=maxDepth, best_keys=best_keys)
    return nMin, resMin, best_keys


def partition(length, flavors=[3,6,7]):
    '''
    this function should return a list of all configurations as dictionary, with the respective multiplicities, the total multiplicity and the residual.
    e.g. for 15
    {
        2: {0: {0: 1}},
        1: {1: {0: 2},
            0: {2: 2,
                1: 5,
                0: 8}},
        0: {2: {1: 0,
                0: 3}}
        ...
    }
    '''
    counter = {}
    
    nMax = int(length/flavors[-1])

    m = len(flavors)
    for i, n in enumerate(reversed(range(nMax+1))):
        residual = length - n*flavors[-1]
        counter[n] = residual
        if residual == 0 or m == 1:
            return counter
        counter[n] = partition(residual, flavors=flavors[:(m-1)])

    return counter

def getPartition(length, flavors=[3,6,7]):

    c = partition(length, flavors)
    res = getN(c, 0, nMin=99, resMin=99, keys=[0,0,0], maxDepth=0, best_keys=[])

    partition_list = []

    for i, flav in enumerate(reversed(flavors)):
        partition_list += [flav]*res[2][i]
    
    del c, res

    return partition_list


