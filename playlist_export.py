"""
SCRIPT TO EXPORT ALL PLAYLISTS OF A SPOTIFY USER
TO A SERIES OF PAGINATED JSON FILES
WITH A DEFAULT OF 100 SONGS A PIECE (API request max limit)
"""
from spotify_functions import *

print("\nThis script will export all playlists of a Spotify user account into paginated JSON files.")
print("It assumes you have already generated the necessary credentials and stored them in './tokens.json'")
print("If you have not, use './get_credentials.py' to generate a new set of credentials")

# reading the credentials to read user private playlists
spotify_credentials = read_jsonfile_as_dict("tokens.json")

if credential_check(desired_scope="playlist-read-private", credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    # get list of playlists
    print("\nRetrieving list of playlists created and followed by the user")

    successful, playlists_df = get_all_playlists_df(access_token=access_token)

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
                                                               output_folder="playlists")
        pages_list.append(number_of_pages)

    playlists_df["pages"] = pd.Series(data=pages_list, index=playlists_df.index)

    try:
        playlists_df.to_csv("playlists/playlists.csv")
        print("\nPlaylist summary df exported to 'playlists/playlists.csv'")

    except:
        print("\nError - Playlist summary df could not be exported")

    print("\nSuccess - Export of user playlists completed")

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)
