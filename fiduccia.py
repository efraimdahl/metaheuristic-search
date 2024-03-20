import networkx as nx
import matplotlib.pyplot as plt
import graph_handler
import copy
import numpy as np
import time
import math 

class DoubleLinkedElement:
    def __init__(self, vertexValue, next, previous, gain):
        self.vertexValue = vertexValue
        self.next = next
        self.previous = previous
        self.gain = gain
    
    def append(self, valueNewNode, gain):
        new = DoubleLinkedElement(vertexValue=valueNewNode, next=self.next, previous=self, gain=gain)
        if (self.next):
            self.next.previous = new
        self.next = new
        return new
        
        
    
    def remove(self): 
        temp = copy.copy(self)
        if (self.next): #check if tail
            self.next.previous = self.previous 
        if (self.previous): #check if head
            self.previous.next = temp.next

    
    def isEmpty(self):
        return not self.next 
    
    def getVertexAsList(self): # Caution this needs O(n)
        res = []
        temp = copy.copy(self)
        while (temp.previous):
            temp = temp.previous
            if (temp.vertexValue ):
                res.append( temp.vertexValue)
            
        if (self.vertexValue):
            res.append(self.vertexValue)
        temp = copy.copy(self)
        while (temp.next):
            temp = temp.next
            if (temp.vertexValue ):
           
                res.append(temp.vertexValue)
            
        return res   





def calculateGain(G:nx.Graph,node)->int:
    """
    The gain is calculated by the amount of connections to nodes of the same, and of the other color. 
    all nodes of the same color subtract from the gain, all nodes of the other color add to the gain

    """
    maxGain = 0
    for nd,connected_node in list(G.edges(node)):
        if(graph_handler.getNodeColor(G,connected_node) == graph_handler.getNodeColor(G,node)):
            maxGain-=1
        else:
            maxGain+=1
    return maxGain


    
def initializeBuckets(G):
    """
    Initializes the gain Buckets by calculating the gains expressed.
    Takes as input the Graph, and the color of the items in the leftBucket
    """
    maxCard = 0
    for vertex in G.nodes:
        maxCard = max(maxCard,G.degree[vertex])
    # its a bit odd, but for the implementation in this way, we start the each Double Linked List with a Element with None value!
    
    lBucket = [DoubleLinkedElement(None, None, None, i) for i in range(0,maxCard*2+1)]
    rBucket = [DoubleLinkedElement(None, None, None, i) for i in range(0,maxCard*2+1)]
    lBucketsize = 0
    rBucketsize = 0
    vertexElementReference = {}
    vertexBucketReference = {}
    #For each node calculate the gain achived by moving the node to the other color, and insert into appropriate index 
    for vertex in G.nodes:
        
        gaindex = calculateGain(G,vertex)+maxCard
        if(graph_handler.getNodeColor(G, vertex) == graph_handler.COLOR_PARTITION_0):
            cell = lBucket[gaindex].append(vertex, gaindex)
            vertexElementReference[vertex] = cell
            vertexBucketReference[vertex] = lBucket
            lBucketsize+=1
        else:
            cell = rBucket[gaindex].append(vertex, gaindex)
            vertexElementReference[vertex] = cell
            vertexBucketReference[vertex] = rBucket
            rBucketsize+=1
    
    return lBucket,rBucket,lBucketsize,rBucketsize, vertexElementReference, vertexBucketReference

#Keep the buckets balanced
def bucketSelect(lBucket, rBucket,lBucketsize,rBucketsize):
    if(lBucketsize>=rBucketsize):
        pickBucket = lBucket
        receiveBucket = rBucket
        pickBucketSize = lBucketsize
        receiveBucketSize=rBucketsize
    else:
        pickBucket = rBucket
        receiveBucket = lBucket
        pickBucketSize = rBucketsize
        receiveBucketSize=lBucketsize
    
    return pickBucket, pickBucketSize, receiveBucket, receiveBucketSize

# returns index and gain from maximum possible move
def findMaximumGain(bucket):
    for i in range(len(bucket) - 1,-1,-1):
        if not (bucket[i].isEmpty()):  # cause there is always a element with None as vertexValue we need to check if it has a next element
                             # if not the bucket entry is empty  
            gain = i
            return gain, bucket[i].next
    return -1,-1   

def popVertrexFromBucket(element, vertexElementReference, vertexBucketReference):
    vertex = element.vertexValue 
    vertexElementReference[vertex] = None  # set to None, because we dont want to move this vertex again
    vertexBucketReference[vertex] = None
    element.remove()
    return vertex   
    
# TODO double check if in O(1)
def updateGain(G, maxGainVertex,vertexBucketReference, vertexElementReference):
    cutUpdate = 0
    for neighborVertex in (G.neighbors(maxGainVertex)):
        
        neighborElement = vertexElementReference[neighborVertex]
        
        # update gain:
        if graph_handler.getNodeColor(G, neighborVertex) == graph_handler.getNodeColor(G, maxGainVertex):
            if neighborElement:                
                gain = neighborElement.gain - 2 # TODOC 
            cutUpdate -= 1                      # TODOC
        else:
            if neighborElement:
                gain = neighborElement.gain + 2
            cutUpdate += 1
        
        if not neighborElement:              # if vertex was already moved we dont need to calculate the gain and add it to our buckets
            continue
        
        neighborElement.remove()          
        neighborElement = vertexBucketReference[neighborVertex][gain].append(neighborVertex, gain)
        vertexElementReference[neighborVertex] = neighborElement 
    return cutUpdate

def findBestPartition(G,  lockedVertices):
    minCut = math.inf
    for v in lockedVertices:
        if v["valid"]:
            minCut = min(minCut, v["cut"])
    for vertex in lockedVertices:
        if (minCut == vertex["cut"] and vertex["valid"]):
            return G, graph_handler.getPartition(G), minCut
        
        vertexColor = graph_handler.getNodeColor(G, vertex["vertex"])
        graph_handler.setNodeColor(G, vertex["vertex"], graph_handler.getComplementColor(vertexColor))
        

# we have to Datastructures, the buckets, and the graph:
# the buckets are a list of double linked lists, the graph is a list of nodes, and a list of edges
# to map this we need a dictionary, that maps the vertex to the element in the bucket (vertexElementReference)
# (this dictionary also helps us to keep track of which elements/vertecies we already moved)
# following i will use element to describe the double linked list element, and vertex to describe the graph node
def fm_pass(G):
        
    """
    performs a single pass of the Fiduccia–Mattheyses algorithm
    """
    lBucket,rBucket,lBucketsize,rBucketsize, vertexElementReference, vertexBucketReference=initializeBuckets(G)
    pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(lBucket, rBucket,lBucketsize,rBucketsize)
   # startPartition = graph_handler.getPartition(G)
    cut = graph_handler.getCut(G)
    lockedVertices = []
    maxGain, maxGainElement = findMaximumGain(pickBucket)
    
    while(maxGain!=-1):
        maxGainVertex = popVertrexFromBucket(maxGainElement, vertexElementReference,vertexBucketReference)
        pickBucketSize = pickBucketSize - 1
        
        partitionColor = graph_handler.getNodeColor(G, maxGainVertex)
        graph_handler.setNodeColor(G,maxGainVertex, graph_handler.getComplementColor(partitionColor))
        
        # O(n) * O(updateGain)
        cut += updateGain(G, maxGainVertex, vertexBucketReference, vertexElementReference)
        if (pickBucketSize == receiveBucketSize):
            lockedVertices.append({"vertex": maxGainVertex, "valid": True, "cut": cut})
        else:
            lockedVertices.append({"vertex": maxGainVertex, "valid": False, "cut": cut})
        
        
        pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(pickBucket, receiveBucket,pickBucketSize,receiveBucketSize)    
        maxGain, maxGainElement = findMaximumGain(pickBucket)

    #endPartition = graph_handler.getPartition(G)
    #assert(graph_handler.getComplement(G, startPartition) == endPartition ) # "fm has different start end partition" 
    lockedVertices.reverse()
    return findBestPartition(G, lockedVertices)
              

def fm_search(G:nx.Graph):

    #Calculate maximum cardinality, maximum amount of edges any one vertex has, this is the maximum gain/loss
    #initialize the gain bucket as dictionary of lists
    all_cuts = []
    lastCut , newPartition, newCut = math.inf,  graph_handler.getPartition(G), 999999999999 
    counter = 0
    while newCut < lastCut:
        lastPartition = newPartition 
        lastCut = newCut
        graph_handler.setPartition(G, lastPartition)
        G , newPartition, newCut = fm_pass(G)
        all_cuts.append(newCut)
        counter += 1
    return G, lastCut, counter, all_cuts

def testDoubleLinkedList():
    # TODO, just praying the foundation datastructure works properly lol...
    head = DoubleLinkedElement(None, None, None)
    item1 = head.append(1)
    item2 = item1.append(2)
    item3 = item2.append(3)
    item0 = head.append(99)
    #item1.remove()
    print(item3.getVertexAsList())



def testFM():
    graphInit = graph_handler.createExampleGraph2()
    print(graph_handler.getStringBinaryRepresentation(graphInit))
    graphResult,lastPartition,_,_ = fm_search(graphInit.copy())
    graph_handler.setPartition(graphResult, lastPartition)
    print(graph_handler.getStringBinaryRepresentation(graphResult))
    graph_handler.vizualizeComparionsGraph(graphInit, graphResult)
    assert(len(graphInit.nodes) == len(graphResult.nodes))
    for node1, node2 in zip(graphInit.nodes, graphResult.nodes):
        assert(node1 == node2)  #node order should not be changed
        #assert(G1.nodes[node1]["color"] != G2.nodes[node1]["color"])  # should be same partition
        
    graphInit = graph_handler.createExampleGraph1()
    graphResult,_,_,_ = fm_search(graphInit.copy())
    graph_handler.vizualizeComparionsGraph(graphInit, graphResult)

    #graphInit = graph_handler.createExampleGraph3()
    #graphResult,_,_,_ = fm_search(graphInit.copy())
    #graph_handler.vizualizeComparionsGraph(graphInit, graphResult)

    graphInit = graph_handler.createExampleGraph4()
    graphResult,_,_,_ = fm_search(graphInit.copy())
    graph_handler.vizualizeComparionsGraph(graphInit, graphResult)

    
    

#testFM()