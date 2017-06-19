import rw
import networkx as nx
import numpy as np
import pickle
import sys

filename=sys.argv[1]

usf_graph, usf_items = rw.read_csv("./snet/USF_animal_subset.snet")
usf_graph_nx = nx.from_numpy_matrix(usf_graph)
usf_numnodes = len(usf_items)

numsubs = 50
numlists = 3
listlength = 35
numsims = 1
#methods=['rw','goni','chan','kenett','fe']
methods=['uinvite']

toydata=rw.Data({
        'numx': numlists,
        'trim': listlength })

fitinfo=rw.Fitinfo({
        'prior_a': 0.5,
        'startGraph': "goni_valid",
        'goni_size': 2,
        'goni_threshold': 2,
        'followtype': "avg", 
        'prune_limit': np.inf,
        'triangle_limit': np.inf,
        'other_limit': np.inf })

#toygraphs=rw.Graphs({
#        'numgraphs': 1,
#        'graphtype': "steyvers",
#        'numnodes': 280,
#        'numlinks': 6,
#        'prob_rewire': .3})

# generate data for `numsub` participants, each having `numlists` lists of `listlengths` items
seednum=0    # seednum=150 (numsubs*numlists) means start at second sim, etc.

for simnum in range(numsims):
    data = []       # Xs using usf_item indices
    datab = []      # Xs using ss_item indices (nodes only generated by subject)
    numnodes = []
    items = []      # ss_items
    startseed = seednum # for recording

    for sub in range(numsubs):
        Xs = rw.genX(usf_graph_nx, toydata, seed=seednum)[0]
        data.append(Xs)

        # renumber dictionary and item list
        itemset = set(rw.flatten_list(Xs))
        numnodes.append(len(itemset))

        ss_items = {}
        convertX = {}
        for itemnum, item in enumerate(itemset):
            ss_items[itemnum] = usf_items[item]
            convertX[item] = itemnum

        items.append(ss_items)

        Xs = [[convertX[i] for i in x] for x in Xs]
        datab.append(Xs)
        
        seednum += numlists

    listnum=10
    uinvite_graphs, priordict = rw.hierarchicalUinvite(datab[:listnum], items[:listnum], numnodes[:listnum], toydata, fitinfo=fitinfo)
    uinvite_group_graph = rw.priorToGraph(priordict, usf_items)

    alldata=dict()
    alldata['uinvite_graphs'] = uinvite_graphs
    alldata['priordict'] = priordict
    alldata['uinvite_group_graph'] = uinvite_group_graph
    alldata['datab'] = datab
    alldata['items'] = items
    alldata['numnodes'] = numnodes
    #alldata['td'] = toydata
    #alldata['fitinfo'] = fitinfo

    fh=open(filename,"w")
    pickle.dump(alldata,fh)
    fh.close()
    
    costlist = [rw.costSDT(uinvite_group_graph, usf_graph), rw.cost(uinvite_group_graph, usf_graph)]
    costlist = rw.flatten_list(costlist)
    for i in costlist:
        print i, ",",

    print rw.probXhierarchical(datab[:listnum], uinvite_graphs[:listnum], items[:listnum], priordict, toydata)