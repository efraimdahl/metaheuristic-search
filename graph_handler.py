import networkx as nx
import matplotlib.pyplot as plt


COLOR_PARTION_1 = "green"
COLOR_PARTION_2 = "red"



#Show Graph:
def vizualize_graph(G):
    pos = nx.spring_layout(G)
    color_map = [G.nodes[node]['color'] for node in G]   
    nx.draw(G, pos, with_labels=True,node_color=color_map)
    plt.show()

def getNodeColor(G, vertex):
    return G.nodes[vertex]["color"]

def getOppositeColor(color):
    if color == COLOR_PARTION_1:
        return COLOR_PARTION_2
    return COLOR_PARTION_1

def getPartion(G):
    return getVerticiesByColor(G, COLOR_PARTION_1)

def setPartion(G, vertices):
    for vertex in G.nodes():
        if vertex in vertices:
            setNodeColor(G,vertex, COLOR_PARTION_1)
        else:
            setNodeColor(G,vertex, COLOR_PARTION_2)

def getVerticiesByColor(G, color): # O(n)
    cutVertexList = []
    for vertex in G.nodes():
        if getNodeColor(G,vertex) == color:    #   TODOC: partition color does not matter, since cut is symetric 
            cutVertexList.append(vertex)
    return cutVertexList


def getCut(G): # O(n) + O(cut_size)
    cutVertexList = []
    for vertex in G.nodes():
        if getNodeColor(G,vertex) == COLOR_PARTION_1:    #   TODOC: partition color does not matter, since cut is symetric 
            cutVertexList.append(vertex)
    
    return nx.cut_size(G, cutVertexList)
    


def setNodeColor(G, vertex, color):
    G.nodes[vertex]["color"] = color

#Parsing Graph
def parse_graph(filename, viz=False):
    G = nx.Graph()
    with open(filename,'r') as file:
        lines = file.readlines()
        vertices = []
        edges = []
        color="blue"
        for line in lines:
            color="red" if color=="blue" else "blue"
            line_info = line.split(" ")
            vertex = int(line_info[0].strip())
            vertices.append((vertex,{"color":color}))
            for i in range(1,int(line_info[2].strip())+1):
                edges.append((vertex,int(line_info[2+i].strip())))
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    if(viz):
        vizualize_graph(G)
    return G

#parse_graph("tests/simpleTest.txt",viz=True)
            