"""
SCRIPT TO READ ALL PLAYLISTS OF AN USER ON YOUTUBE
AND CREATE ONE SPOTIFY PLAYLIST PER YOUTUBE PLAYLIST
WITH THE SONGS IN THEM

    WORK IN PROGRESS!!!
"""

from spotify_functions import *
from youtube_functions import *

# get Spotify credentials and check they are valid to create playlists
spotify_credentials = read_jsonfile_as_dict("spotify_tokens.json")

if spotify_credential_check(required_scopes=["playlist-modify-private"], credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)

    user_id = user_details["id"]

    # get YouTube credentials to be able to browse Youtube playlists
    youtube_secrets = read_jsonfile_as_dict("youtube_secrets.json")
    api_key = youtube_secrets["api_key"]
    channel_id = youtube_secrets["channel_id"]

    # get a list of the user playlists on YouTube
    user_playlists_df = get_df_of_user_playlists(api_key=api_key, channel_id=channel_id, max_results=25)

    print(f"\nList of YouTube playlists found in channel {channel_id}:\n")
    print(f"{user_playlists_df.to_string()}\n")

    # for each playlist found
    for index, row in user_playlists_df.iterrows():

        playlist_id = row["id"]
        playlist_title = row["title"]

        # ask the user if he wants to add this particular YouTube playlist to Spotify
        mod_selector = ""
        while mod_selector not in ("y", "n"):
            print(f"\nDo you want to add the YouTube playlist: {playlist_title} to your Spotify account?")
            mod_selector = input("\nType (y) to add it or (n) to skip it:")
            if mod_selector not in ("y", "n"):
                print("\nError selecting the choice, invalid value given")

        print(f"Input accepted. Your value given: {mod_selector}")

        if mod_selector == "n":
            continue

        # if the user wants to add this playlist to Spotify
        if mod_selector == "y":

            # obtain list of items in playlist
            playlist_items_df = get_df_of_playlist_items(api_key=api_key, playlist_id=playlist_id)

            # retrieve category id of each video to determine which ones are songs
            playlist_items_df["category_id"] = playlist_items_df["videoId"].apply(lambda x: get_video_category_id(api_key=api_key, videoId=x))

            # videos with a category id of "10" are Music
            songs_df = playlist_items_df[playlist_items_df["category_id"] == "10"]

            # create a Spotify playlist

            # search each song on Spotify DB to obtain spotify uri of each track

            # add all songs in the YouTube Playlist that had a match on Spotify DB to the Spotify playlist





