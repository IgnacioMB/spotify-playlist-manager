"""
SCRIPT TO MERGE AND PARSE ALL PAGINATED JSON FILES OF EACH PLAYLIST OF A SPOTIFY USER
INTO CLEAN CSV FILES
"""

from spotify_functions import *

print("\nThis script will merge and parse all paginated json files of each playlist into clean csv files")
print("It assumes you have already extracted all playlists from a Spotify user's account")
print("using the './playlist_export.py' script")

try:
    playlists_df = pd.read_csv("playlists/playlists.csv")
    print("\nPlaylist summary df successfully imported")

    print(f"\nEXPORTED PLAYLISTS: \n\n{playlists_df.to_string()}\n")
except FileNotFoundError:
    print("\nError - Playlist summary df could not be imported")

for index, row in playlists_df.iterrows():

    print(f"\nReading tracks from playlist: {row['name']}")

    playlist_df = pd.DataFrame()

    current_page = 1

    while current_page <= row["pages"]:

        print(f"Parsing page {current_page} out of {row['pages']}...")

        current_filename = f"{row['name']} - {current_page}.json"

        current_json = read_jsonfile_as_dict(f"playlists/{current_filename}")

        current_df = pd.DataFrame(current_json["items"])

        current_df["name"] = current_df["track"].apply(lambda x: x['name'])
        current_df["artists"] = current_df["track"].apply(lambda track: [artist["name"] for artist in track["artists"]])
        current_df['album'] = current_df["track"].apply(lambda x: x["album"]["name"])
        current_df['album_release_date'] = current_df["track"].apply(lambda x: x["album"]["release_date"])
        current_df['album_uri'] = current_df["track"].apply(lambda x: x["album"]["uri"])
        current_df['spotify_uri'] = current_df["track"].apply(lambda x: x["uri"])

        current_df = current_df[['name', 'artists', 'album', 'album_release_date', 'album_uri', 'added_at', 'spotify_uri']]

        playlist_df = pd.concat([playlist_df, current_df])

        if current_page == row["pages"]:

            playlist_df.reset_index(inplace=True)
            playlist_df.drop(labels=['index'], axis=1, inplace=True)
            try:
                playlist_df.to_csv(f"playlists/{row['name']}.csv")
                print("Formatted csv exported correctly")
            except:
                print("Error - Outputting formatted csv failed")

        current_page += 1

print("\nSUCCESS - All playlists where parsed and merged into clean csv files!")

print(f"\nSample of csv output:\n\n{current_df.head().to_string()}")
