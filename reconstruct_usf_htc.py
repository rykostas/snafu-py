import rw
import networkx as nx
import numpy as np
import sys

usf_graph, usf_items = rw.read_csv("snet/USF_animal_subset.snet")
usf_graph_nx = nx.from_numpy_matrix(usf_graph)
usf_numnodes = len(usf_items)

numsubs = int(sys.argv[2])+1
numlists = 3
listlength = 35
numsims = 10
#methods=['rw','goni','chan','kenett','fe']
method="kenett"
methods=[method]        # use one method at a time on htc... this is just to avoid rewriting code

toydata=rw.Data({
        'numx': numlists,
        'trim': listlength })

fitinfo=rw.Fitinfo({
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

outfile=method + "_" + str(numsubs) + ".csv"
with open(outfile,'w',0) as fh:
    fh.write("method,simnum,listnum,hit,miss,fa,cr,cost,startseed\n")

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

        #for listnum in range(1,len(data)+1):
        listnum = numsubs
        print simnum, listnum
        flatdata = rw.flatten_list(data[:listnum])
        if 'rw' in methods:
            rw_graph = rw.noHidden(flatdata, usf_numnodes)
        if 'goni' in methods:
            goni_graph = rw.goni(flatdata, usf_numnodes, td=toydata, valid=0, fitinfo=fitinfo)
        if 'chan' in methods:
            chan_graph = rw.chan(flatdata, usf_numnodes)
        if 'kenett' in methods:
            kenett_graph = rw.kenett(flatdata, usf_numnodes)
        if 'fe' in methods:
            fe_graph = rw.firstEdge(flatdata, usf_numnodes)
        if 'uinvite_hierarchical' in methods:
            uinvite_graphs, priordict = rw.hierarchicalUinvite(datab[:listnum], items[:listnum], numnodes[:listnum], toydata, fitinfo=fitinfo)
	    priordict = rw.genGraphPrior(uinvite_graphs, items, fitinfo=fitinfo, mincount=2)
            uinvite_group_graph = rw.priorToGraph(priordict, usf_items) #JZ
        if 'uinvite_flat' in methods:
            uinvite_flat_graph, ll = rw.uinvite(flatdata, toydata, usf_numnodes, fitinfo=fitinfo)

        for method in methods:
            if method=="rw": costlist = [rw.costSDT(rw_graph, usf_graph), rw.cost(rw_graph, usf_graph)]
            if method=="goni": costlist = [rw.costSDT(goni_graph, usf_graph), rw.cost(goni_graph, usf_graph)]
            if method=="chan": costlist = [rw.costSDT(chan_graph, usf_graph), rw.cost(chan_graph, usf_graph)]
            if method=="kenett": costlist = [rw.costSDT(kenett_graph, usf_graph), rw.cost(kenett_graph, usf_graph)]
            if method=="fe": costlist = [rw.costSDT(fe_graph, usf_graph), rw.cost(fe_graph, usf_graph)]
            if method=="uinvite_hierarchical": costlist = [rw.costSDT(uinvite_group_graph, usf_graph), rw.cost(uinvite_group_graph, usf_graph)]
            if method=="uinvite_flat": costlist = [rw.costSDT(uinvite_flat_graph, usf_graph), rw.cost(uinvite_flat_graph, usf_graph)]
            costlist = rw.flatten_list(costlist)
            fh.write(method + "," + str(simnum) + "," + str(listnum))
            for i in costlist:
                fh.write("," + str(i))
            fh.write("," + str(startseed))
            fh.write('\n')