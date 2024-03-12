
import networkx as nx
import matplotlib.pyplot as plt
import graph_handler
import copy
import numpy as np
import time

class DoubleLinkedElement:
    def __init__(self, vertexValue, next, previous):
        self.vertexValue = vertexValue
        self.next = next
        self.previous = previous
    
    def append(self, valueNewNode):
        new = DoubleLinkedElement(vertexValue=valueNewNode, next=self.next, previous=self)
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
    
    lBucket = [DoubleLinkedElement(None, None, None) for i in range(0,maxCard*2+1)]
    rBucket = [DoubleLinkedElement(None, None, None) for i in range(0,maxCard*2+1)]
    lBucketsize = 0
    rBucketsize = 0
    cellReference = {}
    #For each node calculate the gain achived by moving the node to the other color, and insert into appropriate index 
    for vertex in G.nodes:
        
        gaindex = calculateGain(G,vertex)+maxCard
        if(graph_handler.getNodeColor(G, vertex) == graph_handler.COLOR_PARTION_1):
            cell = lBucket[gaindex].append(vertex)
            cellReference[vertex] = cell
            lBucketsize+=1
        else:
            cell = rBucket[gaindex].append(vertex)
            cellReference[vertex] = cell
            rBucketsize+=1
    
    return lBucket,rBucket,lBucketsize,rBucketsize, cellReference

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
        if(bucket[i].next):  # cause there is always a element with None as vertexValue we need to check if it has a next element
                             # if not the bucket entry is empty  
            gain = i
            return gain, bucket[i].next
    return -1,-1   

def popVertrexFromBucket(element, vertexElementReference):
    vertex = element.vertexValue 
    vertexElementReference[vertex] = None  # set to None, because we dont want to move this vertex again
        
    element.remove()
    return vertex   
    
# TODO double check if in O(1)
def updateGain(G, vertex,bucket, vertexElementReference):
    neighborElement = vertexElementReference[vertex]
    if not neighborElement:              # if vertex was already moved we dont need to calculate the gain and add it to our buckets
        return
    # update gain:
    gain = calculateGain(G, vertex)
    neighborElement.remove()          
    neighborElement = bucket[gain].append(vertex)
    vertexElementReference[vertex] = neighborElement 
# we have to Datastructures, the buckets, and the graph:
# the buckets are a list of double linked lists, the graph is a list of nodes, and a list of edges
# to map this we need a dictionary, that maps the vertex to the element in the bucket (vertexElementReference)
# (this dictionary also helps us to keep track of which elements/vertecies we already moved)
# following i will use element to describe the double linked list element, and vertex to describe the graph node
def fm_pass(G, lBucket, rBucket,lBucketsize,rBucketsize,vertexElementReference, colors=("red","blue")):
    """
    performs a single pass of the Fiduccia–Mattheyses algorithm
    """
    pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(lBucket, rBucket,lBucketsize,rBucketsize)
    
    lockedVertices = []
    cuts = []
    partions = []
    maxGain, maxGainElement = findMaximumGain(pickBucket)
    while(maxGain!=-1):
        maxGainVertex = popVertrexFromBucket(maxGainElement, vertexElementReference)
        lockedVertices.append(maxGainVertex)
        pickBucketSize = pickBucketSize - 1

        partionColor = graph_handler.getNodeColor(G, maxGainVertex)
        graph_handler.setNodeColor(G,maxGainVertex, graph_handler.getOppositeColor(partionColor))
        
        partions.append(graph_handler.getPartion(G)) 
        
        
        # O(n) * O(updateGain)
        for neighborVertex in (G.neighbors(maxGainVertex)):
            updateGain(G,neighborVertex, receiveBucket, vertexElementReference)
        
        cuts.append(graph_handler.getCut(G))
        
        pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(pickBucket, receiveBucket,pickBucketSize,receiveBucketSize)    
        maxGain, maxGainElement = findMaximumGain(pickBucket)


    return G, np.min(cuts), lockedVertices[np.argmin(cuts)], partions[np.argmin(cuts)] 

          

def fm_search(G:nx.Graph):
    #Calculate maximum cardinality, maximum amount of edges any one vertex has, this is the maximum gain/loss
    #initialize the gain bucket as dictionary of lists
    
    lastCut ,lastVertix, lastPartion = 999, None, graph_handler.getPartion(G)
    cut = 998
    while cut < lastCut:
        lastCut = cut
        graph_handler.setPartion(G, lastPartion)
        lBucket,rBucket,lBucketsize,rBucketsize, cellReference=initializeBuckets(G)
        start = time.time()
        G,cut,lastVertix, lastPartion = fm_pass(G,lBucket,rBucket,lBucketsize,rBucketsize, cellReference)
        print(f'fm_pass time: {time.time() - start}')

    return G, lastVertix, lastPartion

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
    graphResult,_,lastPartion = fm_search(graphInit.copy())
    graph_handler.setPartion(graphResult, lastPartion)
    graph_handler.vizualizeComparionsGraph(graphInit, graphResult)
    assert(len(graphInit.nodes) == len(graphResult.nodes))
    for node1, node2 in zip(graphInit.nodes, graphResult.nodes):
        assert(node1 == node2)  #node order should not be changed
        #assert(G1.nodes[node1]["color"] != G2.nodes[node1]["color"])  # should be same partition
        
    graphInit = graph_handler.createExampleGraph1()
    graphResult,_,_ = fm_search(graphInit.copy())
    graph_handler.vizualizeComparionsGraph(graphInit, graphResult)
    

testFM()