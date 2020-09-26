import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

music = pd.read_csv("1142775741/MusicIsLife!.csv")

# we want to group the songs in intervals of max 10 bpm of difference
desired_interval_width = 10

# create the bins for the intervals
min_bpm = music.tempo.min()
max_bpm = music.tempo.max()

num_of_intervals = math.ceil((max_bpm - min_bpm)/desired_interval_width)

bins = np.linspace(min_bpm, max_bpm, num_of_intervals)

# create the frequency distribution table
dist_table = music.tempo.apply(pd.Series.value_counts, bins=bins).sum()

# argmax() does not work properly with interval indices
# so we need a work around to find the top bpm cluster
bpm_clusters = pd.DataFrame(dist_table).reset_index()

bpm_clusters.rename(columns={"index": "bpm_interval", 0: "frequency"}, inplace=True)

bpm_clusters.bpm_interval = bpm_clusters.bpm_interval.astype(str)

bpm_top_cluster = bpm_clusters.loc[bpm_clusters.frequency == bpm_clusters.frequency.max(), "bpm_interval"].values[0]

# store it as a tuple with the lower and upper end of the interval (lower, upper)
bpm_top_cluster = eval(bpm_top_cluster.replace("]", ")"))

# retrieve the songs that fall in the interval
music["in_top_bpm_cluster"] = music.tempo.apply(lambda bpm: (bpm > bpm_top_cluster[0]) and (bpm <= bpm_top_cluster[1]))

top_bpm_cluster_songs = music.loc[music.in_top_bpm_cluster, :].copy()

# order the subset of songs by danceability and take the top 35

top_bpm_cluster_songs.sort_values(by="danceability", ascending=False, inplace=True)

preselection = top_bpm_cluster_songs.head(35).copy()

preselection.to_csv("1142775741/preseleccion_juan.csv")

print("")