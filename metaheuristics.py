
import networkx as nx
import matplotlib.pyplot as plt
import graph_handler
import copy
class GainBucket:
    def __init__(self, value, next, previous):
        self.value = value
        self.next = next
        self.previous = previous
    
    def append(self, valueNewNode):
        new = GainBucket(value=valueNewNode, next=self.next, previous=self)
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
        self = None
    
    def toString(self):
        res = ""
        temp = copy.copy(self)
        while (temp.previous):
            res += self.previous.value
            temp = temp.previous
        res += f"({self.value})"
        temp = copy.copy(self)
        while (temp.next):
            res += f"{temp.next.value}"
            temp = temp.next
        return res    





def calculateGain(G:nx.Graph,node)->int:
    """
    The gain is calculated by the amount of connections to nodes of the same, and of the other color. 
    all nodes of the same color subtract from the gain, all nodes of the other color add to the gain

    """
    maxGain = 0
    for nd,connected_node in list(G.edges(node)):
        if(G.nodes[connected_node]['color']==G.nodes[node]['color']):
            maxGain-=1
        else:
            maxGain+=1
    return maxGain


    
def initializeBuckets(G,lColor='red'):
    """
    Initializes the gain Buckets by calculating the gains expressed.
    Takes as input the Graph, and the color of the items in the leftBucket
    """
    maxCard = 0
    for vertex in G.nodes:
        maxCard = max(maxCard,G.degree[vertex])
    lBucket = [GainBucket("head", None, None) for i in range(0,maxCard*2+1)]
    rBucket = [GainBucket("head", None, None) for i in range(0,maxCard*2+1)]
    lBucketsize = 0
    rBucketsize = 0
    cellReference = {}
    #For each node calculate the gain achived by moving the node to the other color, and insert into appropriate index 
    for vertex in G.nodes:
        
        gaindex = calculateGain(G,vertex)+maxCard
        if(G.nodes[vertex]['color']==lColor):
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
        if(bucket[i].next != None):
            gain = i
            return gain, bucket[i].next
    return -1,-1   


def fm_pass(G, lBucket, rBucket,lBucketsize,rBucketsize,cellReference, colors=("red","blue")):
    """
    performs a single pass of the Fiduccia–Mattheyses algorithm
    """
    pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(lBucket, rBucket,lBucketsize,rBucketsize)
    
   
    maxGain, maxGainVertex = findMaximumGain(pickBucket)
    while(maxGain!=-1):
        maxGainVertex.remove()
        pickBucketSize = pickBucketSize - 1

        vertex = maxGainVertex.value
        cellReference[vertex] = None
        G.nodes[vertex]["color"] = "red" if G.nodes[vertex]["color"] == "green" else "green"   # TODO: make color constants somewhere
        for neighbor in (G.neighbors(vertex)):
            gainBucket = cellReference[neighbor]
            if not gainBucket:
                continue
            gain = calculateGain(G, neighbor)
            gainBucket.remove()
            bucket = receiveBucket[gain].append(neighbor)
            cellReference[neighbor] = bucket 
        pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(pickBucket, receiveBucket,pickBucketSize,receiveBucketSize)    
        maxGain, maxGainVertex = findMaximumGain(pickBucket)

    return G, -1, -1, -1

            

        


    return

def fm_search(G:nx.Graph):
    #Calculate maximum cardinality, maximum amount of edges any one vertex has, this is the maximum gain/loss
    #initialize the gain bucket as dictionary of lists
    lBucket,rBucket,lBucketsize,rBucketsize, cellReference=initializeBuckets(G)
    
    G,lBucket,rBucket,cuts = fm_pass(G,lBucket,rBucket,lBucketsize,rBucketsize, cellReference)
    return G


head = GainBucket("head", None, None)
item1 = head.append(1)
item2 = item1.append(2)
item3 = item2.append(3)
item0 = head.append(0)
item1.remove()
#print(head.toString())


vertices = [('A',{"color":"green",}),('B',{"color":"red",}),('C',{"color":"green",}),('D',{"color":"red",})]
edges = [('A','B'),('B','C'),('B','A'),('C','B'),('B','C'),('C','D'),('D','C')]
G1 = nx.Graph()
G1.add_nodes_from(vertices)
G1.add_edges_from(edges)
graph_handler.vizualize_graph(G1)
G2 = fm_search(G1)
graph_handler.vizualize_graph(G2)
t = 2