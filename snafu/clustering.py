
import numpy as np

# given list of cluster lengths, compute average cluster size of each list, then return avearge of that
# also works on single list
def clusterSize(l, scheme, clustertype='fluid'):
    clist = findClusters(l, scheme, clustertype)
    
    avglists=[]
    for i in clist:
        avglist=[]
        for l in i:
            avglist.append(np.mean(l))
        avglists.append(np.mean(avglist))
    return avglists

# given list of cluster lengths, compute average number of cluster switches of each list, then return avearge of that
# also works on single list
def clusterSwitch(l, scheme, clustertype='fluid'):
    clist = findClusters(l, scheme, clustertype)
    
    avglists=[]
    for i in clist:
        avgnum=[]
        if len(i) > 0:
            if isinstance(i[0], list):
                for l in clist:
                    avgnum.append(len(l)-1)
                avglists.append(np.mean(avgnum))
            else:
                avglists.append(len(i)-1)
        else:
            avglists.append(0)
    return avglists

# report average cluster size for list or nested lists
def findClusters(l, scheme, clustertype='fluid'):
    # only convert items to labels if list of items, not list of lists
    if len(l) > 0:
        if isinstance(l[0], list):
            clusters=l
        else:
            clusters=labelClusters(l, scheme)
    else:
        clusters=[]
    
    csize=[]
    curcats=set([])
    runlen=0
    clustList=[]
    firstitem=1
    for inum, item in enumerate(clusters):
        if isinstance(item, list):
            clustList.append(findClusters(item, scheme, clustertype=clustertype))
        else:
            newcats=set(item.split(';'))
            if 'unknown' in newcats:
                #print("Warning: Unknown category for item '", l[inum], "'. Add this item to your category labels or results may be incorrect!")
                pass
            if newcats.isdisjoint(curcats) and firstitem != 1:      # end of cluster, append cluster length
                csize.append(runlen)
                runlen = 1
            else:                                                   # shared cluster or start of list
                runlen += 1
            
            if clustertype=="fluid":
                curcats = newcats
            elif clustertype=="static":
                curcats = (curcats & newcats)
                if curcats==set([]):
                    curcats = newcats
            else:
                raise ValueError('Invalid cluster type')
        firstitem=0
    csize.append(runlen)
    if sum(csize) > 0:
        clustList += csize
    return clustList

# returns labels in place of items for list or nested lists
# provide list (l) and coding scheme (external file)
def labelClusters(l, scheme):
    if isinstance(scheme,str):
        clustertype = "semantic"    # reads clusters from a fixed file
    elif isinstance(scheme,int):
        clustertype = "letter"      # if an int is given, use the first N letters as a clustering scheme
        maxletters = scheme
    else:
        raise Exception('Unknown clustering type in labelClusters()')

    if clustertype == "semantic":
        cf=open(scheme,'r')
        cats={}
        for line in cf:
            line=line.rstrip()
            if line[0] == "#": continue         # skip commented lines
            cat, item = line.split(',')
            cat=cat.lower().replace(' ','').replace("'","").replace("-","") # basic clean-up
            item=item.lower().replace(' ','').replace("'","").replace("-","")
            if item not in list(cats.keys()):
                cats[item]=cat
            else:
                if cat not in cats[item]:
                    cats[item]=cats[item] + ';' + cat
    labels=[]
    for inum, item in enumerate(l):
        if isinstance(item, list):
            labels.append(labelClusters(item, scheme))
        else:
            item=item.lower().replace(' ','')
            if clustertype == "semantic":
                if item in list(cats.keys()):
                    labels.append(cats[item])
                else:
                    labels.append("unknown")
            elif clustertype == "letter":
                labels.append(item[:maxletters])
    return labels

# broken
def intrusionsList(l, scheme):
    labels=labelClusters(l, scheme)
    if len(l) > 0:
        if isinstance(labels[0], list):
            intrusion_items=[]
            for listnum, nested_list in enumerate(labels):
                intrusion_items.append([l[listnum][i] for i, j in enumerate(nested_list) if j=="unknown"])
        else:
            intrusion_items = [l[i] for i, j in enumerate(labels) if j=="unknown"]
    else:
        intrusion_items = []
    return intrusion_items
  

# broken
def intrusions(l, scheme):
    ilist = intrusionsList(l, scheme)
    
    if isinstance(ilist[0],list):
        return np.mean([len(i) for i in ilist])
    else:
        return len(ilist)

# broken
def perseverationsList(l):
    if len(l) > 0:
        if isinstance(l[0], list):
            perseveration_items=[] 
            for ls in l:
                perseveration_items.append(list(set([item for item in ls if ls.count(item) > 1])))
        else:
            perseveration_items = list(set([item for item in l if l.count(item) > 1]))
    else:
        perseveration_items = []
    return perseveration_items


def perseverations(l):
    if isinstance(l[0][0],list):
        return [np.mean([len(i)-len(set(i)) for i in l2]) for l2 in l]
    else:
        return [len(i)-len(set(i)) for i in l]
