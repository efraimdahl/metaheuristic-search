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
        G, partition, cut, cntFMPass = fiduccia.fm_search(G)
        if cut  < minCut:
            minCut = cut
            bestPartition = partition

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

m = mutatePartition("1111100000", numberOfMutations=2)
graphInit = graph_handler.parse_graph("res/Graph500.txt", True)
mls(graphInit, 10)
print(graph_handler.getStringBinaryRepresentation(graphInit))
graph_handler.vizualize_graph(graphInit)