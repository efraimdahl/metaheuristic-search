
import networkx as nx
import matplotlib.pyplot as plt
import graph_handler
import copy
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
        self = None
    
    def toString(self):
        res = ""
        temp = copy.copy(self)
        while (temp.previous):
            res += self.previous.vertexValue
            temp = temp.previous
        res += f"({self.vertexValue})"
        temp = copy.copy(self)
        while (temp.next):
            res += f"{temp.next.vertexValue}"
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
    lBucket = [DoubleLinkedElement("head", None, None) for i in range(0,maxCard*2+1)]
    rBucket = [DoubleLinkedElement("head", None, None) for i in range(0,maxCard*2+1)]
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
    
   
    maxGain, maxGainElement = findMaximumGain(pickBucket)
    while(maxGain!=-1):
        maxGainElement.remove()
        vertex = maxGainElement.vertexValue 
        vertexElementReference[vertex] = None  # set to None, because we dont want to move this vertex again
        pickBucketSize = pickBucketSize - 1

        G.nodes[vertex]["color"] = "red" if G.nodes[vertex]["color"] == "green" else "green"   # TODO: make color constants somewhere
        
        
        for neighborVertex in (G.neighbors(vertex)):
            neighborElement = vertexElementReference[neighborVertex]
            if not neighborElement:              # if vertex was already moved we dont need to calculate the gain and add it to our buckets
                continue
            # update gain:
            gain = calculateGain(G, neighborVertex)
            neighborElement.remove()          
            neighborElement = receiveBucket[gain].append(neighborVertex)
            vertexElementReference[neighborVertex] = neighborElement 


        pickBucket, pickBucketSize, receiveBucket, receiveBucketSize = bucketSelect(pickBucket, receiveBucket,pickBucketSize,receiveBucketSize)    
        maxGain, maxGainElement = findMaximumGain(pickBucket)

    return G, -1, -1, -1

          

def fm_search(G:nx.Graph):
    #Calculate maximum cardinality, maximum amount of edges any one vertex has, this is the maximum gain/loss
    #initialize the gain bucket as dictionary of lists
    lBucket,rBucket,lBucketsize,rBucketsize, cellReference=initializeBuckets(G)
    
    G,lBucket,rBucket,cuts = fm_pass(G,lBucket,rBucket,lBucketsize,rBucketsize, cellReference)
    return G


head = DoubleLinkedElement("head", None, None)
item1 = head.append(1)
item2 = item1.append(2)
item3 = item2.append(3)
item0 = head.append(0)
item1.remove()
#print(head.toString())


vertices = [('A',{"color":"green",}),('B',{"color":"red",}),('C',{"color":"green",}),('D',{"color":"green"})]
edges = [('A','B'),('B','C'),('B','A'),('C','B'),('B','C'),('C','D'),('D','C')]
G1 = nx.Graph()
G1.add_nodes_from(vertices)
G1.add_edges_from(edges)
graph_handler.vizualize_graph(G1)
G2 = fm_search(G1)
graph_handler.vizualize_graph(G2)
t = 2