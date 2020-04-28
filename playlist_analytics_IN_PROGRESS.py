"""
SCRIPT TO ANALYZE THE SONGS OF A PLAYLIST
AND DRAW INSIGHTS ABOUT THE MUSIC TASTE OF THE USER
BASED ON IT

        ONGOING!!!!! BARELY STARTED EXPLORATORY ANALYSIS
"""

from spotify_functions import *
import matplotlib.pyplot as plt

playlist_name = 'MusicIsLife!'
csv_filename = f"{playlist_name}-enriched.csv"

# read the playlist csv file
playlist_df = read_playlist_csv(csv_filename=csv_filename, folder="enriched_playlists")

# the str field artists that contains the artist names for each song should be evaluated to a list
playlist_df["artists"] = playlist_df["artists"].apply(lambda x: eval(x))

# artist names might contain alphanumeric characters
# that creates problems while generating visualizations
# therefore we strip all non alphanumeric chars from them
playlist_df["artists_stripped"] = playlist_df["artists"].apply(lambda my_list: [only_alphanumeric(item) for item in my_list])

"""
ARTIST INSIGHTS
"""

# calculate top 20 of most popular artists by song count in playlist
unpacked_artist_series = unpack_list_series(playlist_df["artists_stripped"])

artist_frequency_table = unpacked_artist_series.value_counts()

top_20 = artist_frequency_table.head(20)

print("\nTop 20 artists by song count in playlist\n")

print(top_20.to_string())

# analyze concentration of user liked songs per artist

avg_songs_per_artist = artist_frequency_table.mean()
print(f"\nAverage song count per artist in the playlist: {avg_songs_per_artist}")

# plot top 20 artist by song count in playlist as bar plot

fig = plt.figure()

axes = fig.add_axes([0.1, 0.3, 0.8, 0.6])

axes.set_xlabel("Artist")
axes.set_ylabel("Songs in playlist")
axes.set_title(f"Top 20 Artists in Playlist {playlist_name}")

top_20.plot(kind="bar", axes=axes)

plt.show()


print("")