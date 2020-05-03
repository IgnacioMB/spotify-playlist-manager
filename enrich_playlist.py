"""
SCRIPT TO ENRICH A PLAYLIST CSV FILE WITH TRACK AUDIO FEATURES AND ALBUM DETAILS
"""

from spotify_functions import *
import numpy as np

print("\nThis script reads a playlist csv file and enriches it with the audio features of its tracks.")
print("It also adds the album detailed info to each song")
print("The outputs is stored in a new playlist csv file in the './enriched_playlists' folder")

# reading the credentials to read user private playlists
spotify_credentials = read_jsonfile_as_dict("spotify_tokens.json")

if spotify_credential_check(required_scopes=None, credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)
    user_id = user_details["id"]

    # read the playlist csv
    playlist_name, playlist_df = load_playlist_from_input(playlist_folder=user_id)

    audio_feature_list = []
    album_detail_list = []

    for index, row in playlist_df.iterrows():

        # obtain audio features from song
        track_id = row["spotify_uri"].split(":")[2]

        successful, audio_features = get_track_audio_features(track_id=track_id,
                                                              access_token=access_token)

        if not successful:
            audio_features = np.nan

        audio_feature_list.append(audio_features)

        # obtain song's album details
        album_id = row["album_uri"].split(":")[2]
        successful, album_details = get_album_info(album_id=album_id,
                                                   access_token=access_token)

        if not successful:
            album_details = np.nan

        album_detail_list.append(album_details)

    # enrich playlist DataFrame with nested column containing audio feature info
    playlist_df['audio_features'] = pd.Series(data=audio_feature_list, index=playlist_df.index)

    # unpack relevant audio features into individual columns
    playlist_df["danceability"] = playlist_df["audio_features"].apply(lambda x: x["danceability"])
    playlist_df["energy"] = playlist_df["audio_features"].apply(lambda x: x["energy"])
    playlist_df["key"] = playlist_df["audio_features"].apply(lambda x: x["key"])
    playlist_df["loudness"] = playlist_df["audio_features"].apply(lambda x: x["loudness"])
    playlist_df["mode"] = playlist_df["audio_features"].apply(lambda x: x["mode"])
    playlist_df["speechiness"] = playlist_df["audio_features"].apply(lambda x: x["speechiness"])
    playlist_df["acousticness"] = playlist_df["audio_features"].apply(lambda x: x["acousticness"])
    playlist_df["instrumentalness"] = playlist_df["audio_features"].apply(lambda x: x["instrumentalness"])
    playlist_df["liveness"] = playlist_df["audio_features"].apply(lambda x: x["liveness"])
    playlist_df["valence"] = playlist_df["audio_features"].apply(lambda x: x["valence"])
    playlist_df["tempo"] = playlist_df["audio_features"].apply(lambda x: x["tempo"])
    playlist_df["duration_ms"] = playlist_df["audio_features"].apply(lambda x: x["duration_ms"])

    # drop nested column after processing
    playlist_df.drop(labels=["audio_features"], axis=1, inplace=True)

    # enrich playlist DataFrame with nested column containing album detailed info
    playlist_df['album_details'] = pd.Series(data=album_detail_list, index=playlist_df.index)

    # unpack relevant album info into individual columns
    playlist_df['album_type'] = playlist_df['album_details'].apply(lambda x: x["album_type"])
    playlist_df['album_genres'] = playlist_df['album_details'].apply(lambda x: x["genres"])
    playlist_df['album_popularity'] = playlist_df['album_details'].apply(lambda x: x["popularity"])
    playlist_df['album_total_tracks'] = playlist_df['album_details'].apply(lambda x: x["total_tracks"])

    # drop nested column after processing
    playlist_df.drop(labels=["album_details"], axis=1, inplace=True)

    # export enriched df
    export_playlist_csv(playlist_name, playlist_df, user_id)

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)

print()
