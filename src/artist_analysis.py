#!/usr/bin/env python
# encoding: utf-8


""" REFERENCE:
Boriah, S., Chandola, V., & Kumar, V. (2008). Similarity measures for
categorical data: A comparative evaluation. Society for Industrial and
Applied Mathematics - 8th SIAM International Conference on Data Mining 2008,
Proceedings in Applied Mathematics 130, 1, 243–254.
https://doi.org/10.1137/1.9781611972788.22
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from collections import Counter
from itertools import combinations
from scipy import stats
from mannwhitney import mannWhitney


INPUT = "../data/ARTIST/ArtistsFeatures_20201105.csv"
# INPUT = "../data/BOTH/ArtistsFeatures_20201202.csv"


def goodall_distance(df):
    """
    """
    N = df.shape[0]

    # Compute the frequency of each attribute's values
    DictFreqAttr = {}
    for col in df.columns:
        DictFreqAttr[col] = Counter(df[col])

    # Compute the probability of each attribute's values
    DictPropAttr = {}
    for attr in DictFreqAttr:
        DictPropAttr[attr] = {}
        for val in DictFreqAttr[attr]:
            DictPropAttr[attr][val] = DictFreqAttr[attr][val] / N

    # Compute the probability^2 of each attribute's values
    DictPropAttr2 = {}
    for attr in DictFreqAttr:
        DictPropAttr2[attr] = {}
        for val in DictFreqAttr[attr]:
            DictPropAttr2[attr][val] = (
                DictFreqAttr[attr][val]*(
                    DictFreqAttr[attr][val]-1)) / (N*(N-1))

    # Compute Goodall 1
    DictSimAttr = {}
    for attr in DictPropAttr2:
        DictSimAttr[attr] = {}
        for val in DictPropAttr2[attr]:
            DictSimAttr[attr][val] = 1 - sum(
                [DictPropAttr2[attr][x] for x in DictPropAttr2[attr]
                    if DictPropAttr2[attr][x] <= DictPropAttr2[attr][val]])

    # Create Similarity/Distance Matrix
    out = np.zeros((N, N))
    distances = []
    for c in combinations(range(N), 2):
        s = 0
        for attr in DictSimAttr:
            if df.iloc[c[0]][attr] == df.iloc[c[1]][attr]:
                s += (1 / df.shape[1]) * DictSimAttr[attr][df.iloc[c[0]][attr]]
        distances.append(1 - s)
        out[c[0], c[1]] = out[c[1], c[0]] = 1 - s

    return out, distances  

if __name__ == '__main__':

    df = pd.read_csv(INPUT)

    out, distances = goodall_distance(df)


    # ### Group distances by List ###
    dist_groups = []
    c = 0
    while c<32:
        T = np.triu(out[c:c+4, c:c+4])
        dist_groups.append(T[T>0])
        c+=4
    plt.boxplot(dist_groups)
    # plt.show()

    # ### Compute Stats for Group ###
    print()
    meds = []
    for dists in dist_groups:
        print("{:.2f} {:.2f} {:.2f}".format(min(dists), np.mean(dists), stats.mstats.gmean(dists)))

        
    ### Mann-Whitney-U test ###
    print("\n### Mann-Whitney-U test ###")
    print("List 1-2")
    MU = mannWhitney(dist_groups[0], dist_groups[1])
    print(np.median(dist_groups[0]), np.median(dist_groups[1]))
    print("Significance: {}; U-statistics: {}, EffectSize: {}\n".format(
                                        MU.significance, MU.u, MU.effectsize))

    print("List 3-4")
    MU = mannWhitney(dist_groups[2], dist_groups[3])
    print(np.median(dist_groups[2]), np.median(dist_groups[3]))
    print("Significance: {}; U-statistics: {}, EffectSize: {}\n".format(
                                        MU.significance, MU.u, MU.effectsize))    
    print("List 5-6")
    MU = mannWhitney(dist_groups[4], dist_groups[5])
    print(np.median(dist_groups[4]), np.median(dist_groups[5]))
    print("Significance: {}; U-statistics: {}, EffectSize: {}\n".format(
                                        MU.significance, MU.u, MU.effectsize))    
    
    print("List 7-8")
    MU = mannWhitney(dist_groups[6], dist_groups[7])
    print(np.median(dist_groups[6]), np.median(dist_groups[7]))
    print("Significance: {}; U-statistics: {}, EffectSize: {}\n".format(
                                        MU.significance, MU.u, MU.effectsize))   


