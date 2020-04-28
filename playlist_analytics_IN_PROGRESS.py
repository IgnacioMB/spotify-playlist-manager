"""
SCRIPT TO ANALYZE THE SONGS OF A PLAYLIST
AND DRAW INSIGHTS ABOUT THE MUSIC TASTE OF THE USER
BASED ON IT

        ONGOING!!!!! BARELY STARTED EXPLORATORY ANALYSIS
"""

from spotify_functions import *

playlist_name = 'MusicIsLife!'
csv_filename = f"{playlist_name}-enriched.csv"

# read the playlist csv file
playlist_df = read_playlist_csv(csv_filename=csv_filename, folder="enriched_playlists")


"""
ARTIST INSIGHTS
"""

# calculate top of most popular artists
unpacked_artist_series = unpack_list_series(playlist_df["artists"])

artist_frequency_table = unpacked_artist_series.value_counts()

print("\nTop 20 artists by song count in playlist\n")

print(artist_frequency_table.head(20).to_string())

# analyze concentration of user liked songs per artist

avg_songs_per_artist = artist_frequency_table.mean()

print(f"\nAverage song count per artist in the playlist: {avg_songs_per_artist}")

artist_frequency_table.plot(kind="hist", bins=20)

print("")