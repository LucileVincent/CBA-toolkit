import matplotlib.pyplot as plt

def gantt_corresponding_segments(dct, lstA, lstB):
    """visualize segments of tiers in a gant graph.
    Colors alternate between successive segments.
    Same colors for both corresponding segments."""

    _, ax = plt.subplots()
    ypos = [1,0.5]
    id_col = -1
    col = {-1:"blue", 1:"orange"}
    for indA, B in dct.items():
        widthA = lstA[indA][1] - lstA[indA][0]
        leftA = lstA[indA][0]
        for indB in B:
            widthB = lstB[indB][1] - lstB[indB][0]
            leftB = lstB[indB][0]
            ax.barh(y = ypos, width = [widthA, widthB], left = [leftA, leftB], height = 0.1, color = col[id_col])
        id_col *= -1
    first = list(dct.keys())[0]
    last = list(dct.keys())[-1]
    ax.set_yticks(ypos)
    ax.set_yticklabels(["A", "B"])
    plt.xlim([lstA[first][0]-0.1*lstA[first][0], lstA[last][1]+0.1*lstA[last][1]])
    plt.show()
    return

def gantt(dct):
    """visualize segments of tiers in a gant graph.
    dct is a dict of name:list"""
    _, ax = plt.subplots()
    y=1
    ticks_pos = []
    ticks_names = []
    for name, lst in dct.items():
        if len(lst) == 0:
            continue
        for (strt, stp, lab) in lst:
            width = stp-strt
            ax.barh(y, width = width, left = strt, height = 0.1, color = "blue")
        ticks_pos.append(y)
        ticks_names.append(name)
        y+=1
    ax.set_yticks(ticks_pos)
    ax.set_yticklabels(ticks_names)
    plt.show()
    return