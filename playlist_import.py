"""
SCRIPT TO READ THE CSV FILE OF A PLAYLIST AND IMPORT IT INTO A SPOTIFY USER'S ACCOUNT

It adds them in inverse order of addition to the original playlist (latest songs up)
"""

from spotify_functions import *
import sys

print("\nThis script will import a playlist (in csv) into a Spotify user's account")

# read the credentials to modify user private playlists
spotify_credentials = read_jsonfile_as_dict("tokens.json")

if credential_check(required_scopes=["playlist-modify-private"], credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)

    user_id = user_details["id"]

    # read the playlist csv file
    playlist_name, playlist_df = load_playlist_from_input(playlist_folder=user_id)

    playlist_df.sort_values(by="added_at", ascending=True, inplace=True)

    new_playlist_name = playlist_name + " copy"

    created, details = create_playlist(user_id=user_id,
                                       access_token=access_token,
                                       name=new_playlist_name,
                                       public=False,
                                       collaborative=False,
                                       description=f"This is a copy of the playlist {playlist_name}")

    new_playlist_id = details["id"]

    for index, row in playlist_df.iterrows():

        added, details = add_song_to_playlist(playlist_id=new_playlist_id,
                                              access_token=access_token,
                                              song_uri=row["spotify_uri"],
                                              position=0)

        if added:
            print(f"Song: {row['name']} added to playlist {new_playlist_name} successfully")

        else:
            print(f"Error - Song: {row['name']} could not be added to playlist {new_playlist_name}")

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)

print(f"\nSUCCESS - Import of playlist {playlist_name} completed")
