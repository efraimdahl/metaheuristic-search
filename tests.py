vertices = [('A',{"color":"green",}),('B',{"color":"red",}),('C',{"color":"green",}),('D',{"color":"red",})]
edges = [('A','B'),('B','C'),('B','A'),('C','B'),('B','C'),('C','D'),('D','C')]
G1 = nx.Graph()
G1.add_nodes_from(vertices)
G1.add_edges_from(edges)
vizualize_graph(G1)

print(calculateGain(G1,'A'))
assert(calculateGain(G1,'A')==1)
assert(calculateGain(G1,'B')==2)
assert(calculateGain(G1,'C')==2)
assert(calculateGain(G1,'D')==1)

assert(initializeBuckets(G1,lColor="green")==([[], [], [], ['A'], ['C']], [[], [], [], ['D'], ['B']],2,2))
assert(bucketSelect([[], [], [], ['A'], ['C']], [[], [], [], ['D'], ['B']],2,2)==([[], [], [], ['A'], ['C']],2,[[], [], [], ['D'], ['B']],2))
assert(bucketSelect([[], [], [], [], ['C']], [[], [], ['B'], ['D'], ['A']],1,3)==([[], [], ['B'], ['D'], ['A']],3,[[], [], [], [], ['C']],1))
assert(bucketSelect([[], [], ['B'], ['A'], ['C']], [[], [], [], ['D'], []],3,1)==([[], [], ['B'], ['A'], ['C']],3,[[], [], [], ['D'], []],1))
