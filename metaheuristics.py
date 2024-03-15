import fiduccia
import graph_handler 
import networkx as nx
import random
import math
import numpy as np


def createRandomPartition(G):
    binStr = graph_handler.BINARY_PARTITION_0 * int(len(G.nodes()) / 2)
    binStr += graph_handler.BINARY_PARTITION_1 * int(len(G.nodes()) / 2)
    binList = list(binStr)
    random.shuffle(binList)
    return binList

def mls(G, numberRandoms = 10, maxFMPasses= 10000):
    bestPartition = None
    minCut = math.inf 
    fmCounter = 0
    for run in range(numberRandoms):
        binList = createRandomPartition(G)
        graph_handler.setPartitionByBinaryList(G, binList)
        G, partition, cut, cntFMPass = fiduccia.fm_search(G)
        fmCounter += cntFMPass
        if cut  < minCut:
            minCut = cut
            bestPartition = partition
        if fmCounter >  maxFMPasses:
            return graph_handler.setPartition(G, bestPartition) 

    graph_handler.setPartition(G, bestPartition) 



def mutatePartition(binStr, numberOfMutations = 1):
    assert( numberOfMutations <= (len(binStr) / 2))
    binArray = np.array(list(binStr))
    partition0Indicies = np.where(binArray == graph_handler.BINARY_PARTITION_0)[0]
    partition1Indicies = np.where(binArray == graph_handler.BINARY_PARTITION_1)[0]
    
    partition0mutations = np.random.choice(partition0Indicies, numberOfMutations, replace=False) 
    partition1mutations = np.random.choice(partition1Indicies, numberOfMutations, replace=False) 

    res = graph_handler.BINARY_PARTITION_0 * len(binStr)
    res = list(res)
    for p1 in partition1Indicies:
        if not p1 in partition1mutations:
            res[p1] = graph_handler.BINARY_PARTITION_1
    for p0 in partition0mutations:
        res[p0] = graph_handler.BINARY_PARTITION_1
    for p1 in partition1mutations:
        res[p1] = graph_handler.BINARY_PARTITION_0

    return "".join(str(s) for s in res)

def ils(G, startNumberOfMutations = 4, maxFmPasses = 10000):
    
    isImproved = True
    solution = createRandomPartition(G)
    graph_handler.setPartitionByBinaryList(G, list(solution))
    G, lastPartition, lastCut, fmCounter = fiduccia.fm_search(G)
    isFMCntMaxReached = False
    while isImproved and not isFMCntMaxReached:
        solution = graph_handler.getStringBinaryRepresentation(G)
        mutatedSolution = mutatePartition(solution, numberOfMutations=startNumberOfMutations)
        graph_handler.setPartitionByBinaryList(G, list(mutatedSolution))
        G, newPartition, newCut, cntFMPass = fiduccia.fm_search(G)
        fmCounter += cntFMPass 
        isImproved = newCut < lastCut
        if isImproved:
            lastCut = newCut
            graph_handler.setPartition(G, newPartition)
        isFMCntMaxReached = fmCounter > maxFmPasses
        
            


    return G, lastPartition, lastCut
    


graphInit = graph_handler.parse_graph("res/Graph500.txt", False)
G, _, cut = ils(graphInit, 10)
print(cut)
#print(graph_handler.getStringBinaryRepresentation(graphInit))
graph_handler.vizualize_graph(graphInit)