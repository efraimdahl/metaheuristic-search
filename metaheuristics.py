import fiduccia
import graph_handler 
import networkx as nx
import random
import math
import numpy as np
import time

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
    startTime = time.time()
    for run in range(numberRandoms):
        binList = createRandomPartition(G)
        graph_handler.setPartitionByBinaryList(G, binList)
        G, partition, cut, cntFMPass = fiduccia.fm_search(G)
        fmCounter += cntFMPass
        if cut  < minCut:
            minCut = cut
            bestPartition = partition
        if fmCounter >  maxFMPasses:
            graph_handler.setPartition(G, bestPartition) 
            return minCut, time.time() - startTime
    graph_handler.setPartition(G, bestPartition) 
    return G, minCut, time.time() - startTime
    




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

def ils(G, startNumberOfMutations = 4, maxFmPasses = 10000, maxTime = None, partition = None):
    
    isImproved = True
    if not partition:
        partition = createRandomPartition(G)
    graph_handler.setPartitionByBinaryList(G, list(partition))
    G, lastPartition, lastCut, fmCounter = fiduccia.fm_search(G)
    isFMCntMaxReached = False
    isMaxTimeReached = False
    startTime = time.time()
    while isImproved and not isFMCntMaxReached and not isMaxTimeReached:
        partition = graph_handler.getStringBinaryRepresentation(G)
        mutatedSolution = mutatePartition(partition, numberOfMutations=startNumberOfMutations)
        graph_handler.setPartitionByBinaryList(G, list(mutatedSolution))
        G, newPartition, newCut, cntFMPass = fiduccia.fm_search(G)
        fmCounter += cntFMPass 
        isImproved = newCut < lastCut
        if isImproved:
            lastCut = newCut
            graph_handler.setPartition(G, newPartition)
        isFMCntMaxReached = fmCounter > maxFmPasses
        if maxTime:
            isMaxTimeReached = (time.time() - startTime) >  maxTime
        
            


    return G, lastCut, fmCounter, time.time() -startTime
    
graphInit = graph_handler.parse_graph("res/Graph500.txt", False)

G, mlsCut, runTimeMLS = mls(graphInit.copy())
G,_, ilsCut, runTimeILS = ils(graphInit.copy(), 5,maxTime=runTimeMLS)

print(f"MLS Cut: {mlsCut}")
print(f"ILS Cut: {ilsCut}")
#print(graph_handler.getStringBinaryRepresentation(graphInit))
graph_handler.vizualize_graph(graphInit)