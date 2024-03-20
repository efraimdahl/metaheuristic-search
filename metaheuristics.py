import fiduccia
import graph_handler 
import networkx as nx
import random
import math
import numpy as np
import time
import graph_handler as gh
import fiduccia as fm
import networkx as nx
import numpy as np
import bisect
MAX_COUNT = 10000
MAX_NO_IMPROV = 20


def createRandomPartition(G):
    binStr = graph_handler.BINARY_PARTITION_0 * int(len(G.nodes()) / 2)
    binStr += graph_handler.BINARY_PARTITION_1 * int(len(G.nodes()) / 2)
    binList = list(binStr)
    random.shuffle(binList)
    return binList

def mls(G, maxFmPasses= 10000):
    bestPartition = None
    cuts = []
    minCut = math.inf   
    fmCounter = 0
    startTime = time.time()
    while fmCounter < maxFmPasses:
        binList = createRandomPartition(G)
        graph_handler.setPartitionByBinaryList(G, binList)
        G, partition, cut, cntFMPass, allCuts = fiduccia.fm_search(G)
        fmCounter += cntFMPass
        cuts.append(allCuts)
        if cut  < minCut:
            minCut = cut
            bestPartition = partition
        
    graph_handler.setPartition(G, bestPartition) 
    return G, cuts, time.time() - startTime
    




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

def ils(G, startNumberOfMutations = 4, maxFmPasses = 10000, maxTime = None, partition = None):
    
    isImproved = True
    if not partition:
        partition = createRandomPartition(G)
    cuts = []
    graph_handler.setPartitionByBinaryList(G, list(partition))
    G, lastPartition, lastCut, fmCounter, allCuts = fiduccia.fm_search(G)
    cuts.append(allCuts)
    isFMCntMaxReached = False
    isMaxTimeReached = False
    startTime = time.time()
    while not isFMCntMaxReached and not isMaxTimeReached:
        partition = graph_handler.getStringBinaryRepresentation(G)
        mutatedSolution = mutatePartition(partition, numberOfMutations=startNumberOfMutations)
        graph_handler.setPartitionByBinaryList(G, list(mutatedSolution))
        G, newPartition, newCut, cntFMPass, allCuts = fiduccia.fm_search(G)
        fmCounter += cntFMPass 
        cuts.append(allCuts)
        isImproved = newCut < lastCut
        if isImproved:
            lastCut = newCut
            graph_handler.setPartition(G, newPartition)
        if maxFmPasses:
            isFMCntMaxReached = fmCounter > maxFmPasses
        if maxTime:
            isMaxTimeReached = (time.time() - startTime) >  maxTime
        
            
        

    return G, cuts, fmCounter, time.time() -startTime
    

def hemming_distance(p1,p2):
    return sum([0 if p1[i]==p2[i] else 1 for i in range (0,len(p1))])

def invert_binary_list(p):
    return ["0" if p[i]=="1" else "1" for i in range(0,len(p))]

def uniformCrossover(p1,p2):
    hd=hemming_distance(p1,p2)
    if(hd>(len(p1)//2)):
        p2 = invert_binary_list(p2)
    balance = 0
    child = [-1]*len(p1)
    for i in range(0,len(p1)):
        if(abs(balance)>=len(p1)-i):
            ci = "0" if balance>0 else "1"
            incr = 1 if balance<0 else -1
            child[i]=ci
            balance+=incr
        elif(p1[i]==p2[i]):
            child[i] = p1[i]
            incr = 1 if p1[i]=="1" else -1
            balance+=incr
        else:
            apnd = np.random.choice([0,1])
            child[i]=str(apnd)
            incr = 1 if apnd==1 else -1
            balance+=incr
    assert(len(child)==len(p1) and balance==0)
    return child

"""
Places the first (non-sorted) item of the list in the correct position, shifting all other elements
"""
def insert(lst, item):
    #print(lst,item)
    # Searching for the position
    index=0
    for i in range(len(lst)-1,-1,-1):
      #print(i,lst[i],item)
      if lst[i][1] < item[1]:
        index = i+1
        break
    # Inserting n in the list
    if index == 0:
      lst = [item]+lst
    else:
      lst = lst[:index] + [item] + lst[index:]
    return lst


"""
The specific genetic algorithm is an incremental (or steady state) GA where there is no
explicit notion of generations: each iteration two parents are randomly selected, use
uniform crossover to generate one child, do FM local search on the child, let this
optimized child compete with the worst solution in the population, if it is better or
equal it replaces the worst solution.

Additional break, after 20 generations of no improvement in best cut, or cut average, the algorithm is stopped.
"""

def geneticSearch(G:nx.Graph,population:int, maxFmPass = 10000):
    res,cntr,no_improv,prev_best,best_avg = [],0,0,np.inf,np.inf
    totalCuts = []
    #randomly initiate vertices in different colors
    pop=[[createRandomPartition(G),np.inf] for i in range(0,population)]
    #calculate number of cuts for each population member
    for mem in pop:
        gh.setPartitionByBinaryList(G,mem[0])
        cut=gh.getCut(G)
        if(cut<prev_best):
            prev_best=cut
        mem[1]=cut
    #print(pop)
    #sort according to cutNumber
    pop.sort(key=lambda x: x[1])
    #print("Population",pop)
    while (cntr<maxFmPass):
        #print(len(pop),population,pop)
        assert(len(pop)==population)
        #randomly select two parents
        p1=np.random.randint(0,population-1)
        p2=p1
        while p2==p1: #makes sure parents are distinct
            p2=np.random.randint(0,population-1)
        child = uniformCrossover(pop[p1][0],pop[p2][0])
        #print(f"child {child} {pop[p1],pop[p2]}" )
        gh.setPartitionByBinaryList(G,child)
        #Improve the child through local search
        G, lastPartition,  lastCut, counter, allCuts=fm.fm_search(G)
        totalCuts.append(allCuts)
        binaryPart = gh.getListBinaryRepresentation(G)
        cntr+=counter
        #Compete with weakest population member
        #print("partition",binaryPart)
        if(lastCut<pop[-1][1]):
            pop.pop()#constant time removal of weakest member
            #print("Population1",pop)
            #print("Inserting",binaryPart,lastCut)
            pop=insert(pop,[binaryPart,lastCut]) #Linear time insert while maintining sorted status    
            #print("Population2",pop)
        minCut = pop[0][1]
        values = [x[1] for x in pop]
        # Calculate the mean
        average = np.mean(values)
        res.append([minCut,average])
        if(minCut>prev_best):
            print([item[1] for item in pop])
        assert(not minCut>prev_best)
        if(prev_best<=minCut and average<=best_avg):
            no_improv+=1
        else:
            no_improv=0
            if(best_avg>average):
                best_avg=average
            if(prev_best>minCut):
                prev_best=minCut
        #if(no_improv>=MAX_NO_IMPROV):
        #    break
    return(res,cntr,pop[0][0], totalCuts)

    #G, partion, cut = fiduccia.fm_search(G)
