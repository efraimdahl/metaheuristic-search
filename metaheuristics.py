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

def mls(G, numberRandoms = 10):
    bestPartition = None
    minCut = math.inf 
    for run in range(numberRandoms):
        binList = createRandomPartition(G)
        graph_handler.setPartitionByBinaryList(G, binList)
        G, partion, cut, cntFMPass = fiduccia.fm_search(G)
        if cut  < minCut:
            minCut = cut
            bestPartition = partion

    graph_handler.setPartition(G, bestPartition) 



def mutatePartition(binStr, numberOfMutations = 1):
    assert( numberOfMutations <= (len(binStr) / 2))
    binArray = np.array(list(binStr))
    partion0Indicies = np.where(binArray == graph_handler.BINARY_PARTITION_0)[0]
    partion1Indicies = np.where(binArray == graph_handler.BINARY_PARTITION_1)[0]
    
    partion0mutations = np.random.choice(partion0Indicies, numberOfMutations, replace=False) 
    partion1mutations = np.random.choice(partion1Indicies, numberOfMutations, replace=False) 

    res = graph_handler.BINARY_PARTITION_0 * len(binStr)
    res = list(res)
    for p1 in partion1Indicies:
        if not p1 in partion1mutations:
            res[p1] = graph_handler.BINARY_PARTITION_1
    for p0 in partion0mutations:
        res[p0] = graph_handler.BINARY_PARTITION_1
    for p1 in partion1mutations:
        res[p1] = graph_handler.BINARY_PARTITION_0

    partion0Indicies = np.where(res == graph_handler.BINARY_PARTITION_0)[0]
    partion1Indicies = np.where(res == graph_handler.BINARY_PARTITION_1)[0]
    
    assert(len(partion0Indicies) == len(partion1Indicies))
    return "".join(str(s) for s in res)


graphInit = graph_handler.parse_graph("res/Graph500.txt", True)
mls(graphInit, 10)
print(graph_handler.getStringBinaryRepresentation(graphInit))
graph_handler.vizualize_graph(graphInit)