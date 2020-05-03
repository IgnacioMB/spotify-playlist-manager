"""
SCRIPT TO EXPORT ALL PLAYLISTS OF A SPOTIFY USER
TO CSV FILES
"""
from spotify_functions import *

print("\nThis script will export all playlists of a Spotify user account into .csv files.")
print("It assumes you have already generated the necessary credentials and stored them in './spotify_tokens.json'")
print("If you have not, use './get_credentials.py' to generate a new set of credentials")

# reading the credentials
spotify_credentials = read_jsonfile_as_dict("spotify_tokens.json")

if spotify_credential_check(required_scopes=["playlist-read-private", "user-library-read"],
                            credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)

    user_id = user_details["id"]

    # get list of playlists
    print(f"\nRetrieving list of playlists created and followed by the user {user_id}")

    successful, playlists_df = spotify_get_all_playlists_df(access_token=access_token)

    if successful:
        print("\nSuccess: User playlists:\n")
        print(f"\n{playlists_df.to_string()}\n")

    else:
        print("\nError: Failed to read user playlists:\n")
        sys.exit(1)

    pages_list = []

    # export playlists tracks to numerated json files
    for index, row in playlists_df.iterrows():

        successful, number_of_pages = export_playlist_to_jsons(track_count=row['track_count'],
                                                               playlist_id=row['id'],
                                                               access_token=access_token,
                                                               playlist_name=row['name'],
                                                               output_folder="temp")
        pages_list.append(number_of_pages)

    playlists_df["pages"] = pd.Series(data=pages_list, index=playlists_df.index)

    # parsing of json files into csv files
    for index, row in playlists_df.iterrows():
        playlist_name = row['name']
        playlist_pages = row["pages"]

        playlist_df = playlist_jsons_to_csv(playlist_name=playlist_name,
                                            playlist_pages=playlist_pages,
                                            jsons_folder="temp")

        export_playlist_csv(playlist_name=playlist_name,
                            playlist_df=playlist_df,
                            output_folder=user_id)

    # extract liked songs playlist (not considered a user playlist by Spotify)
    ls_playlist_name = 'Liked Songs'
    ls_successful, ls_number_of_pages = export_user_added_tracks_to_jsons(playlist_name=ls_playlist_name,
                                                                          access_token=access_token,
                                                                          output_folder="temp")

    liked_songs_df = playlist_jsons_to_csv(playlist_name=ls_playlist_name,
                                           playlist_pages=ls_number_of_pages,
                                           jsons_folder="temp")

    export_playlist_csv(playlist_name=ls_playlist_name,
                        playlist_df=liked_songs_df,
                        output_folder=user_id)

    print(f"\nSuccess - Export of user {user_id} playlists completed")
    print(f"\nOutput folder: {user_id}")

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)
