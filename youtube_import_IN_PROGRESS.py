"""
SCRIPT TO READ ALL PLAYLISTS OF AN USER ON YOUTUBE
AND CREATE ONE SPOTIFY PLAYLIST PER YOUTUBE PLAYLIST
WITH THE SONGS IN THEM

    WORK IN PROGRESS!!!
"""

from spotify_functions import *
from youtube_functions import *
import youtube_dl
pd.options.mode.chained_assignment = None

# get Spotify credentials and check they are valid to create playlists
spotify_credentials = read_jsonfile_as_dict("spotify_tokens.json")

if spotify_credential_check(required_scopes=["playlist-modify-private"], credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)

    user_id = user_details["id"]
    user_name = user_details["display_name"]

    # get YouTube credentials to be able to browse Youtube playlists
    youtube_secrets = read_jsonfile_as_dict("youtube_secrets.json")
    api_key = youtube_secrets["api_key"]
    channel_id = youtube_secrets["channel_id"]

    print(f"\nThis script will import playlists from the YouTube Channel {channel_id} to the Spotify Account of {user_name}.")
    print("For each YouTube playlist found in the channel, the script will ask you if you want to import it to Spotify.")
    print("If you import a playlist, the script will fetch the music videos and ignore the rest.")
    print("It will then search each music video in Spotify's DB and add the matches to your imported Spotify palylist\n")

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

            print(f"\nSongs found in the playlist:\n {songs_df.to_string()}\n")

            # create a Spotify playlist
            new_playlist_name = playlist_title + "  (imported from YouTube)"

            print(f"\nCreating new Spotify playlist {new_playlist_name}\n")

            created, details = spotify_create_playlist(user_id=user_id,
                                                       access_token=access_token,
                                                       name=new_playlist_name,
                                                       public=False,
                                                       collaborative=False,
                                                       description=f"This is a copy of the YouTube playlist {playlist_title}")

            new_playlist_id = details["id"]

            # use youtube_dl to obtain the name of the artist and the song name parsed for us
            songs_df["video_url"] = songs_df["videoId"].apply(lambda video_id: f"https://www.youtube.com/watch?v={video_id}")

            songs_df["artist"] = songs_df["video_url"].apply(
                lambda x: youtube_dl.YoutubeDL({}).extract_info(url=x,
                                                                download=False)["artist"])

            songs_df["song_name"] = songs_df["video_url"].apply(
                lambda x: youtube_dl.YoutubeDL({}).extract_info(url=x,
                                                                download=False)["track"])

            # search each song on Spotify DB to obtain spotify uri of each track
            print(f"\nSearching for songs in Youtube playlist {playlist_title} in the Spotify DB\n")

            songs_df["spotify_uri"] = songs_df.apply(lambda row: get_song_uri(access_token=access_token, song_name=row["song_name"], artist=row["artist"]), axis=1)

            # add all songs in the YouTube Playlist that had a match on Spotify DB to the Spotify playlist
            print(f"\nAddings songs in Youtube playlist {playlist_title} to the Spotify playlist {new_playlist_name}\n")
            songs_df.dropna(subset=["spotify_uri"], axis=0, inplace=True)

            for index, row in songs_df.iterrows():

                added, details = add_song_to_playlist(playlist_id=new_playlist_id,
                                                      access_token=access_token,
                                                      song_uri=row["spotify_uri"])

                if added:
                    print(f"Song: {row['song_name']} added to playlist {new_playlist_name} successfully")

                else:
                    print(f"Error - Song: {row['song_name']} could not be added to playlist {new_playlist_name}")

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)

print(f"\nSUCCESS - Import of YouTube playlists completed")
