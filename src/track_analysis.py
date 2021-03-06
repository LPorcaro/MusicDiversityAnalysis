#!/usr/bin/env python
# encoding: utf-8

import json
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import matplotlib.patches as mpatches

from itertools import combinations
from scipy.optimize import curve_fit
from scipy.spatial.distance import cosine, euclidean, pdist, squareform
from scipy import stats
from matplotlib import cm
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from mannwhitney import mannWhitney

HEADER_HL = ['danceable', 'not_danceable',
            'aggressive', 'not_aggressive',
            'happy', 'not_happy',
            'party', 'not_party', 
            'relaxed', 'not_relaxed',
            'sad','not_sad',
            'bright', 'dark',
            'atonal', 'tonal',
            'instrumental', 'voice']

HEADER_LL = ['average_loudness',
             'barkbands_crest_mean', 'barkbands_crest_std',
             'barkbands_flatness_db_mean', 'barkbands_flatness_db_std',
             'barkbands_kurtosis_mean', 'barkbands_kurtosis_std', 
             'barkbands_skewness_mean',  'barkbands_skewness_std',
             'barkbands_spread_mean', 'barkbands_spread_std', 
             'dissonance_mean', 'dissonance_std', 
             'dynamic_complexity', 
             'erbbands_crest_mean', 'erbbands_crest_std',
             'erbbands_flatness_db_mean', 'erbbands_flatness_db_std', 
             'erbbands_kurtosis_mean', 'erbbands_kurtosis_std', 
             'erbbands_skewness_mean', 'erbbands_skewness_std',
             'erbbands_spread_mean', 'erbbands_spread_std', 
             'hfc_mean', 'hfc_std',
             'melbands_crest_mean', 'melbands_crest_std',
             'melbands_flatness_db_mean', 'melbands_flatness_db_std', 
             'melbands_kurtosis_mean', 'melbands_kurtosis_std', 
             'melbands_skewness_mean', 'melbands_skewness_std', 
             'melbands_spread_mean', 'melbands_spread_std', 
             'pitch_salience_mean', 'pitch_salience_std', 
             'silence_rate_30dB_mean', 'silence_rate_30dB_std',
             'silence_rate_60dB_mean', 'silence_rate_60dB_std',
             'spectral_centroid_mean', 'spectral_centroid_std',  
             'spectral_decrease_mean', 'spectral_decrease_std', 
             'spectral_energy_mean', 'spectral_energy_std', 
             'spectral_energyband_high_mean', 'spectral_energyband_high_std', 
             'spectral_energyband_low_mean', 'spectral_energyband_low_std', 
             'spectral_energyband_middle_high_mean', 'spectral_energyband_middle_high_std', 
             'spectral_energyband_middle_low_mean',  'spectral_energyband_middle_low_std', 
             'spectral_entropy_mean',  'spectral_entropy_std', 
             'spectral_flux_mean', 'spectral_flux_std', 
             'spectral_kurtosis_mean', 'spectral_kurtosis_std', 
             'spectral_rms_mean', 'spectral_rms_std', 
             'spectral_rolloff_mean', 'spectral_rolloff_std', 
             'spectral_skewness_mean', 'spectral_skewness_std', 
             'spectral_strongpeak_mean', 'spectral_strongpeak_std', 
             'zerocrossingrate_mean','zerocrossingrate_std',
             "chords_changes_rate",
             "chords_number_rate",
             "chords_strength_mean","chords_strength_std",
             'hpcp_crest_mean','hpcp_crest_std',
             'hpcp_entropy_mean','hpcp_entropy_std',
             "tuning_diatonic_strength",
             "tuning_equal_tempered_deviation",
             "tuning_frequency",
             "tuning_nontempered_energy_ratio",
             'onset_rate',
             'bpm']

HIGH_LEVEL = [
              "danceability",
              "mood_aggressive",
              "mood_happy",
              "mood_party",
              "mood_relaxed",
              "mood_sad",
              "timbre",
              "tonal_atonal",
              "voice_instrumental",
              ]

LOW_LEVEL = ['average_loudness',
             'barkbands_crest', 
             'barkbands_flatness_db', 
             'barkbands_kurtosis', 
             'barkbands_skewness', 
             'barkbands_spread', 
             'dissonance', 
             'dynamic_complexity', 
             'erbbands_crest', 
             'erbbands_flatness_db', 
             'erbbands_kurtosis', 
             'erbbands_skewness', 
             'erbbands_spread', 
             'hfc', 
             'melbands_crest', 
             'melbands_flatness_db', 
             'melbands_kurtosis', 
             'melbands_skewness', 
             'melbands_spread', 
             'pitch_salience', 
             'silence_rate_30dB',
             'silence_rate_60dB',
             'spectral_centroid', 
             'spectral_decrease', 
             'spectral_energy', 
             'spectral_energyband_high', 
             'spectral_energyband_low', 
             'spectral_energyband_middle_high', 
             'spectral_energyband_middle_low', 
             'spectral_entropy', 
             'spectral_flux', 
             'spectral_kurtosis', 
             'spectral_rms', 
             'spectral_rolloff', 
             'spectral_skewness', 
             'spectral_strongpeak', 
             'zerocrossingrate']

TONAL = ["chords_changes_rate",
         "chords_number_rate",
         "chords_strength",
         "hpcp_crest", 
         "hpcp_entropy",
         "tuning_diatonic_strength",
         "tuning_equal_tempered_deviation",
         "tuning_frequency",
         "tuning_nontempered_energy_ratio"]



def gaussian(x, mean, amplitude, standard_deviation):
    return amplitude * np.exp( - ((x - mean) / standard_deviation) ** 2)


def extract_features(outfile, high_level):
    """
    """
    with open(outfile, 'w+') as outf:
        _writer = csv.writer(outf)

        HEADER = HEADER_LL
        if high_level:
            HEADER = HEADER_HL

        _writer.writerow(HEADER)

        for file in sorted(os.listdir(IN_FOLDER)):
            print("Processing:",file)
            infile = os.path.join(IN_FOLDER, file)

            # Import json
            with open(infile) as f:
                d = json.load(f)

            FeatDict = {}

            if high_level:
                for feat in HIGH_LEVEL:
                    FeatDict = {**FeatDict, **d["highlevel"][feat]["all"]}
                # Write out
                _writer.writerow([FeatDict[x] for x in HEADER])
            else:
                for feat in LOW_LEVEL:
                    try:
                        FeatDict["_".join([feat,"mean"])] = d["lowlevel"][feat]["mean"]
                        FeatDict["_".join([feat,"std"])] = d["lowlevel"][feat]["stdev"]
                    except:
                        FeatDict[feat] = d['lowlevel'][feat]

                for feat in TONAL:
                    try:
                        FeatDict["_".join([feat,"mean"])] = d["tonal"][feat]["mean"]
                        FeatDict["_".join([feat,"std"])] = d["tonal"][feat]["stdev"]
                    except:
                        FeatDict[feat] = d['tonal'][feat]


                FeatDict["onset_rate"] = d['rhythm']['onset_rate'] 
                FeatDict["bpm"] = d['rhythm']['bpm']


                # Write out
                _writer.writerow([FeatDict[x] for x in HEADER])


    print("Done!\n")

def analyze_features(featfile, plot):
    """
    """
    plt.style.use('seaborn-whitegrid')

    df = pd.read_csv(featfile)
    # Apply Power Tranform
    pt = MinMaxScaler()
    df = pd.DataFrame(pt.fit_transform(df), columns=df.columns)  

    # ### Boxplots order by IQR ###
    IQR = df.quantile(0.75)-df.quantile(0.25)
    IQR.sort_values(ascending=False, inplace=True)
    df_plot = df[IQR.index]
    df_plot.boxplot()
    plt.xticks(rotation=90, fontsize = 15)
    plt.tight_layout()
    if plot:
        plt.show()

    # Compute distances
    distances = pdist(df, 'cosine')
    out = squareform(distances)



    # ### Group distances by List ###
    dist_groups = []
    c = 0
    while c<32:
        T = np.triu(out[c:c+4, c:c+4])
        dist_groups.append(T[T>0])
        c+=4
    plt.boxplot(dist_groups)
    if plot:
        plt.show()

    # ### Compute Stats for Group ###
    print()
    meds = []

    for dists in dist_groups:
        print("{:.3f} {:.2f} {:.2f}".format(min(dists), np.mean(dists), stats.mstats.gmean(dists)))


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
    



if __name__ == '__main__':

    task = "BOTH"
    IN_FOLDER = "../data/essentia_extractor_music/{}".format(task)

    high_level = True
    plot = False
    extract = False

    file_attr = "Low"

    if high_level:
        file_attr = "High"

    features_file = "../data/{}/Feat{}_20210113.csv".format(task, file_attr)
    
    if not os.path.exists(features_file):
        extract_features(features_file, high_level)

    analyze_features(features_file, plot)
