import networkx as nx
import matplotlib.pyplot as plt
import re

COLOR_PARTION_0 = "green"
COLOR_PARTION_1 = "red"
BINARY_PARTION_0 = "0"
BINARY_PARTION_1 = "1"
# O(n)
def getStringBinaryRepresentation(G):
    res = ""
    for vertex in G.nodes():
        if getNodeColor(G, vertex) == COLOR_PARTION_0:
            res += BINARY_PARTION_0
        else:
            res += BINARY_PARTION_1
    return res
# O(n)
def setPartionByBinaryList(G, binList):
    for vertex, bit in zip(G.nodes(), binList):
        if bit == BINARY_PARTION_0:
            setNodeColor(G,vertex, COLOR_PARTION_0)
        else:
            setNodeColor(G,vertex, COLOR_PARTION_1)

#Show Graph:
def vizualize_graph(G):
    pos = nx.spring_layout(G)
    color_map = [G.nodes[node]['color'] for node in G]   
    
    nx.draw(G, pos, with_labels=True,node_color=color_map)
    plt.show()

def vizualizeComparionsGraph(GLeft,GRight):
    G=nx.grid_2d_graph(2,1) 
    plt.subplot(221)
    pos = nx.spring_layout(GLeft)
    color_map = [GLeft.nodes[node]['color'] for node in GLeft]   
    nx.draw(GLeft, pos, with_labels=True,node_color=color_map)
    plt.subplot(222)
    pos = nx.spring_layout(GRight)
    color_map = [GRight.nodes[node]['color'] for node in GRight]   
    nx.draw(GRight, pos, with_labels=True,node_color=color_map)
    
    plt.show()

def getNodeColor(G, vertex):
    return G.nodes[vertex]["color"]

def getComplementColor(color):
    if color == COLOR_PARTION_0:
        return COLOR_PARTION_1
    return COLOR_PARTION_0



def getPartion(G):
    return getVerticiesByColor(G, COLOR_PARTION_0)

def setPartion(G, vertices):
    for vertex in G.nodes():
        if vertex in vertices:
            setNodeColor(G,vertex, COLOR_PARTION_0)
        else:
            setNodeColor(G,vertex, COLOR_PARTION_1)

def getVerticiesByColor(G, color): # O(n)
    cutVertexList = []
    for vertex in G.nodes():
        if getNodeColor(G,vertex) == color:    #   TODOC: partition color does not matter, since cut is symetric 
            cutVertexList.append(vertex)
    return cutVertexList


def getCut(G): # O(n) + O(cut_size)
    cutVertexList = []
    for vertex in G.nodes():
        if getNodeColor(G,vertex) == COLOR_PARTION_0:    #   TODOC: partition color does not matter, since cut is symetric 
            cutVertexList.append(vertex)
    
    return nx.cut_size(G, cutVertexList)
    
def getComplement(G, verticies):
    res = []
    for vertex in G.nodes():
        if not vertex in verticies:
            res.append(vertex)
    return res


def setNodeColor(G, vertex, color):
    G.nodes[vertex]["color"] = color

#Parsing Graph
def parse_graph(filename, viz=False):
    G = nx.Graph()
    with open(filename,'r') as file:
        lines = file.readlines()
        vertices = []
        edges = []
        
        for line in lines:
            removedMultiBlanks = re.sub(r'\s+', ' ', line)
            line_info = removedMultiBlanks.split(" ")
            line_info = [i for i in line_info if i != ""]
            vertex = int(line_info[0].strip())
            vertices.append((vertex,{"color":"blue"}))
            for i in range(1,int(line_info[2].strip())+1):
                edges.append((vertex,int(line_info[2+i].strip())))
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    if(viz):
        vizualize_graph(G)
    return G

def createExampleGraph1():
    vertices = [('A',{"color":"green",}),('B',{"color":"red",}),('C',{"color":"red",}),('D',{"color":"green"}, )]
    edges = [('A','B'),('A','C'),('B','C'),('B','A'),('C','B'),('B','C'),('C', 'A') , ('C','D'),('D','C')]
    return createGraph(vertices, edges) 

def createExampleGraph2():
    vertices = [('A',{"color":"green",}),('B',{"color":"red",}),('C',{"color":"green",}),('D',{"color":"red"}, )]
    edges = [('A','B'),('B','C'),('B','A'),('C','B'),('B','C'), ('C','D'),('D','C')]
    return createGraph(vertices, edges) 

def createExampleGraph3():
    vertices = [('A',{"color":"red",}),('B',{"color":"red",}),('C',{"color":"red",}),('D',{"color":"green"}, )]
    edges = [('A','B'),('A','C'),('B','C'),('B','A'),('C','B'),('B','C'),('C', 'A') , ('C','D'),('D','C')]
    return createGraph(vertices, edges) 

def createGraph(vertices, edges):
    G = nx.Graph()
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    return G
#parse_graph("tests/simpleTest.txt",viz=True)
            