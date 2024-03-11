import networkx as nx
import matplotlib.pyplot as plt

#Show Graph:
def vizualize_graph(G):
    pos = nx.spring_layout(G)
    color_map = [G.nodes[node]['color'] for node in G]   
    nx.draw(G, pos, with_labels=True,node_color=color_map)
    plt.show()


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
            