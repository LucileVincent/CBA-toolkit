#low levels
def get_overlapping_segments_ind(lstA, lstB):
    """Get segments in A and B that overlap.
    
    Args:
        lstA (list of tuples): [(start time, stop time, lab),..].
        lstB (list of tuples): [(start time, stop time, lab),..]
    
    Returns
        dict: {index of segment in lstA: [indices of segments in lstB]}
    """

    indA = 0
    indB = 0
    dct = {}
    while indA < len(lstA) and indB < len(lstB):
        while lstA[indA][0] >= lstB[indB][1]:
            indB += 1
            if indB >= len(lstB):
                return dct
        while lstA[indA][1] <= lstB[indB][0]:
            indA += 1
            if indA >= len(lstA):
                return dct
        if (lstA[indA][1] > lstB[indB][1] > lstA[indA][0]) or (
            lstA[indA][1] > lstB[indB][0] > lstA[indA][0]
        ):
            while indB < len(lstB) and lstB[indB][1] < lstA[indA][1]:
                if indA in dct:
                    dct[indA].append(indB)
                else:
                    dct[indA] = [indB]
                indB += 1
            indA += 1
        elif (lstB[indB][0] <= lstA[indA][0]) and (lstB[indB][1] >= lstA[indA][1]):
            while indA < len(lstA) and lstA[indA][1] < lstB[indB][1]:
                if indA in dct:
                    dct[indA].append(indB)
                else:
                    dct[indA] = [indB]
                indA += 1
            indB += 1
    return dct


def overlapping_dct_from_indices_to_vals(dct_inds, lstA, lstB):
    """Convert dictionary of indices to dictionary of values.
    
    Args:
        dct_inds ([type]): output of get_overlapping_segments_ind output.
        lstA ([type]): list of labels only and not [(start, stop, label), etc.]
        lstB ([type]): list of labels only and not [(start, stop, label), etc.]
    
    Returns:
        dict: {val: [vals]}
    """

    dct_vals = {}
    for indA, B in dct_inds.items():
        dct_vals[lstA[indA]] = [lstB[indB] for indB in B]
    return dct_vals


def get_overlapping_segments(lstA, lstB, values_only = False):
    """Get segments in lstB overlapping with segments of lstA.
    
    Args:
        lstA ([type]): [(start, stop, label), etc.]
        lstB ([type]): [(start, stop, label), etc.]
        values_only (bool, optional): [description]. Defaults to False.
    
    Returns:
        dict: {Segments in A: [Segments in B]}
    """
    dct_inds = get_overlapping_segments_ind(lstA, lstB)
    if values_only:
        lstA_tempo = [val for b, e, val in lstA]
        lstB_tempo = [val for b, e, val in lstB]
    else:
        lstA_tempo = lstA[:]
        lstB_tempo = lstB[:]
    dct = overlapping_dct_from_indices_to_vals(dct_inds, lstA_tempo, lstB_tempo)
    return dct

#high levels
def count_mimicry(tA, tB, delta_t=0):
    """Count the occurences of B mimicking A by delta_t.
   
    This implementation counts mimicry based on method in [1]
    and also returns the instances of mimickry.

    The times in each of tA and tB cannot overlap internally.
    They have to be successive segments in each of tA and tB.

    [1] Feese, Sebastian, et al. "Quantifying behavioral mimicry by automatic 
    detection of nonverbal cues from body motion." 2012 International Conference 
    on Privacy, Security, Risk and Trust and 2012 International Conference on 
    Social Computing. IEEE, 2012.
    
    Args:
        tA (list): list of tuples (start, stop, label) of expressions mimicked.
        tB (list): list of tuples (start, stop, label) of expressions mimicking.
        delta_t (int, optional): Defaults to 0.
                                Time after which expression occuring still counts as mimicry.
                                Should be in the same unit as the times in tA and tB.    
    Returns:
        int: number of times B mimicked A (=len(the list described below)).
        list: [(indA, indB),...]
              where the indB element of B mimick the indA element of A
              following the definition of mimickry described in the reference above.
    """

    indA = 0
    indB = 0
    count = 0 # number of mimicry events
    mimic_ind = [] # indices of mimicry events in tB
    while (indA<len(tA) and indB<len(tB)):
        if tB[indB][0]<=tA[indA][0]:
            indB+=1
        elif (tB[indB][0]>tA[indA][0] and (tB[indB][0]-delta_t)<=tA[indA][1]):
            #avoid double counting incase delta_t is > (tA[indA+1][0] - tA[indA][1])
            if (indA+1)<len(tA):
                if tB[indB][0]>tA[indA+1][0]:
                    indA+=1#skip to next tA expression
                    continue
            count+=1
            mimic_ind.append((indA,indB))
            #if no double counting
            #check if several expressions from B overlap with A's
            while tB[indB][1]<=tA[indA][1]:
                indB+=1 #skip to the following expression untill no more overlapping
                if indB == len(tB):
                    break
            indA+=1
        elif ((tB[indB][0]-delta_t)>tA[indA][1]):
            indA+=1
    return count, mimic_ind

def count_mimicry_per_value_in_tier(ref, target, delta_t):
    """Return the number of times mimicry occured.
    
    Considers that all expresssions in ref and target are the same.
    So all are potential mimicry events.

    Args:
        ref (dict): dictionary of values in tier being mimicked.
        target (dict): dictionary of values in tier containing mimicry events.
        delta_t (float): time after which expression occuring still counts as mimicry.
                        Should be in the same unit as the times in ref and target.
    
    Raises:
        AttributeError: [description]
    
    Returns:
        [type]: [description]
    """

    final = {}
    if len(set(ref)) != len(ref):
        raise AttributeError("No parameter is allowed in the parameter ref")
    for r in ref:
        final[r] = {}
        for tar in target:
            final[r][tar] = count_mimicry(ref[r], target[tar], delta_t = delta_t)
    return final

def calculate_mimicking_ratio(total_mimicker_expressions, total_mimicked_expressions):
    """Return the ratio of the total number of expression that are mimicking to 
    the total number of a certain expression.
    
    Args:
        total_mimicker_expr ([type]): [description]
        total_mimicked_expressions ([type]): [description]
    
    Returns:
        [type]: [description]
    """

    return total_mimicked_expressions/total_mimicker_expressions

def following_expressions(lst, delta_t=0):
    """succession of expressions in tier"""
    dct = {}
    for l in range(len(lst)-1):
        if (lst[l+1][0] - lst[l][1]) <= delta_t:
            if lst[l][2] in dct:
                dct[lst[l][2]].append(lst[l+1])
            else:
                dct[lst[l][2]] = [lst[l+1]]
        else:
            if lst[l][2] in dct:
                dct[lst[l][2]].append(None)
            else:
                dct[lst[l][2]] = [None]
    return dct

def count_vals_in_tier(lst, vals_to_count = None):
    dct = {}
    for lab in lst:
        if lab is not None:
            lab = lab[2]
        
        if lab in dct:
            dct[lab]+=1
        else:
            dct[lab]=1
    return dct

def calculate_correlation(lstA, lstB):
    pass

def count_following(lst, n, max_distance):
    labs = set([l for _,_,l in lst])
    dct = {}
    for l in labs:
        dct[l] = {}
    for i in range(len(lst)-n):
        if lst[i][2] not in dct:
            dct[lst[i][2]] = {}
        if (lst[i+n][0] - lst[i][1]) <= max_distance:
            for j in range(1, n+1):
                dct[lst[i][2]][j]={}
                if lst[i+j][2] not in dct[lst[i][2]][j]:
                    dct[lst[i][2]][j][lst[i+j][2]] = 0
                dct[lst[i][2]][j][lst[i+j][2]] += 1
    return dct

def get_next_n_exp(lst, n, max_distance, append_none = True):
    dct = {}
    for l in range(len(lst)-n):#skip the last n elements (cannot assume they are None)
        lab = lst[l][2]
        if lab not in dct:
            dct[lab] = []
        temp = []
        for ind_next in range(1,n+1):
            next_close = lst[l+ind_next-1][1]
            next_far = lst[l+ind_next][0]
            if (next_far-next_close)<=max_distance:
                temp.append(lst[l+ind_next][2])
            else:
                if append_none:
                    temp.extend([None]*(n-ind_next+1))
                break
        if len(temp)==n:
            dct[lab].append(temp)
    return dct

def get_prev_n_exp(lst, n, max_distance, append_none = True):
    dct = {}
    for l in range(n, len(lst)):#skip the first n elements (cannot assume they are None)
        lab = lst[l][2]
        if lab not in dct:
            dct[lab] = []
        temp = []
        for ind_next in range(1,n+1):
            prev_close = lst[l-ind_next+1][0]
            prev_far = lst[l-ind_next][1]
            if (prev_close-prev_far)<=max_distance:
                temp.append (lst[l-ind_next][2])
            else:
                if append_none:
                    temp.extend([None]*(n-ind_next+1))
                break
        if len(temp)==n:
            dct[lab].append(temp)
    return dct