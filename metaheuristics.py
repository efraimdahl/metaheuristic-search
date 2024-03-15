import fiduccia
import graph_handler 
import networkx as nx
import random
import math

def createRandomPartion(G):
    binStr = graph_handler.BINARY_PARTION_0 * int(len(G.nodes()) / 2)
    binStr += graph_handler.BINARY_PARTION_1 * int(len(G.nodes()) / 2)
    binList = list(binStr)
    random.shuffle(binList)
    return binList

def mls(G, numberRandoms = 10):
    bestPartion = None
    minCut = math.inf 
    for run in range(numberRandoms):
        binList = createRandomPartion(G)
        graph_handler.setPartionByBinaryList(G, binList)
        G, partion, cut, cntFMPass = fiduccia.fm_search(G)
        if cut  < minCut:
            minCut = cut
            bestPartion = partion

    graph_handler.setPartion(G, bestPartion) 


graphInit = graph_handler.parse_graph("res/Graph500.txt", True)
mls(graphInit, 10)
print(graph_handler.getStringBinaryRepresentation(graphInit))
graph_handler.vizualize_graph(graphInit)