"""
PROJECT FUNCTIONS
"""

import pandas as pd
import json
import datetime
import sys
import requests
import re
import os


def read_jsonfile_as_dict(filename):

    """
    Reads a json file and returns a dictionary
    :param filename: string with path and filename i.e. "./folder/file.json"
    :return: a dictionary
    """
    try:
        with open(filename) as json_file:
            json_dict = json.load(json_file)
    except FileNotFoundError:
        print(f"\nJSON file '{filename}' could not be found!")
        sys.exit(1)

    return json_dict


def credential_check(required_scope, credentials_dict):

    """

    Takes the desired scope of the credentials and the json object with the credentials
    and checks for validity of the scope and expiration time of the credentials.

    Returns boolean
    If everything ok returns True, of not False and outputs error to console

    :param required_scope: string with the scope i.e. 'playlist-read-private'
    :param credentials_dict: dictionary with the credentials i.e.

    {
    "access_token": "Yr45wSw",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "AQcKSc",
    "scope": "playlist-modify-private",
    "creation_time": "2020-04-25 15:04:54",
    "expiration_time": "2020-04-25 16:04:54"
    }
    :return:
    """

    check = True

    scope = credentials_dict["scope"]
    expiration_time = datetime.datetime.strptime(credentials_dict["expiration_time"], "%Y-%m-%d %H:%M:%S")

    # scope check
    if required_scope in scope:
        print("\nScope check approved")

    else:
        print(f"\nScope check failed - Scope needed: {required_scope} Scope found: {scope}")
        check = False

    # expiration check
    current_time = datetime.datetime.now()

    # if the credentials are expired we fail the test
    if current_time < expiration_time:
        print("Expiration check approved\n")

    else:
        print("Expiration check failed - credentials are expired.\n")
        print("Use './get_credentials.py' to generate a new set of credentials")
        check = False

    return check


def get_all_playlists_df(access_token):

    """
    Reads the catalogue of playlists created or followed by the user and returns it as a DataFrame
    :param access_token: string
    :return: DataFrame
    """

    successful = False

    query = "https://api.spotify.com/v1/me/playlists"

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:

        successful = True

        playlists_json = response.json()

        playlists_df = pd.DataFrame(playlists_json['items'])

        playlists_df["track_count"] = playlists_df["tracks"].apply(lambda x: x["total"])

        playlists_df = playlists_df[["id", "name", "track_count"]]

        output = playlists_df

    else:
        print(f"\nError while requesting list of playlists - Status code: {response.status_code}")
        output = None

    return successful, output


def export_playlist_to_jsons(track_count, playlist_id, access_token, playlist_name, output_folder):

    """
    Exports a given playlist to a series of paginated JSON files
    :param output_folder: str with the path
    :param track_count: int total number of songs in the playlist
    :param playlist_id: str unique identifier of the playlist onf Spotify
    :param access_token: str has to be valid and have the scope 'playlist-read-private'
    :param playlist_name: str name of the playlist
    :return: a boolean indicating success and outputs the json files to a folder and an integer with number of pages
    """

    successful = False

    limit = 100  # set to the max allowed by API
    offset = 0

    full_pages = track_count // limit

    if track_count % limit > 0:
        partial_pages = 1
    else:
        partial_pages = 0

    number_of_pages = full_pages + partial_pages

    current_page = 1

    while current_page <= number_of_pages:

        query = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        query += f"?limit={limit}"
        query += f"&offset={offset}"

        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url=query, headers=headers)

        if response.status_code == 200:

            successful = True

            current_playlist_json = response.json()

            with open(f"{output_folder}/{playlist_name} - {current_page}.json", mode="w+") as output:
                json.dump(current_playlist_json, output)

            offset += limit
            current_page += 1

        else:
            print(f"Error while exporting tracks of playlist {playlist_name} - Status code: {response.status_code}")
            break

    print(f"Playlist {playlist_name} exported successfully to paginated json files")

    return successful, number_of_pages


def playlist_jsons_to_csv(playlist_name, playlist_pages, jsons_folder):

    """
    Reads the paginated json files of a playlist
    and combines them into a DataFrame with all the playlist tracks

    :param playlist_name: str
    :param playlist_pages: int with number of paginated json files
    :param jsons_folder: path to where json files are stored
    :return: a DataFrame with all the tracks
    """

    print(f"\nReading tracks from playlist: {playlist_name}")

    playlist_df = pd.DataFrame()

    current_page = 1

    while current_page <= playlist_pages:

        print(f"Parsing page {current_page} out of {playlist_pages}...")

        current_filename = f"{playlist_name} - {current_page}.json"

        current_json = read_jsonfile_as_dict(f"{jsons_folder}/{current_filename}")

        current_df = pd.DataFrame(current_json["items"])

        current_df["name"] = current_df["track"].apply(lambda x: x['name'])
        current_df["artists"] = current_df["track"].apply(lambda track: [artist["name"] for artist in track["artists"]])
        current_df['album'] = current_df["track"].apply(lambda x: x["album"]["name"])
        current_df['album_release_date'] = current_df["track"].apply(lambda x: x["album"]["release_date"])
        current_df['album_uri'] = current_df["track"].apply(lambda x: x["album"]["uri"])
        current_df['spotify_uri'] = current_df["track"].apply(lambda x: x["uri"])

        current_df = current_df[['name', 'artists', 'album', 'album_release_date', 'album_uri', 'added_at', 'spotify_uri']]

        playlist_df = pd.concat([playlist_df, current_df])

        if current_page == playlist_pages:

            playlist_df.reset_index(inplace=True)
            playlist_df.drop(labels=['index'], axis=1, inplace=True)
            return playlist_df

        else:
            current_page += 1


def export_playlist_csv(playlist_name, playlist_df, output_folder):
    """
    Exports a given playlist to a csv file with all the tracks
    :param playlist_df: DataFrame
    :param output_folder: str
    :return:
    """

    # if the output folder does not exist, we create it
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    try:
        playlist_df.to_csv(f"{output_folder}/{playlist_name}.csv")
        print("\nFormatted csv exported correctly")
    except:
        print(f"\nError - Outputting playlist csv for {playlist_name} failed")


def get_spotify_profile_details(access_token):
    """
    Returns a dictionary with the profile details of the user identified by the token

    :param access_token: string with a Spotify authentification token
    :return: dictionary
    """

    query = "https://api.spotify.com/v1/me"

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:

        return response.json()

    else:
        print(f"Error - Request for user profile details failed - Status code: {response.status_code}")


def create_playlist(user_id, access_token, name, public, collaborative, description):
    """
    Creates a playlist in the user account identified by the user_id

    If there is another playlist with the same name existing it stills creates a new one

    :param user_id: string with the user id
    :param access_token: string with valid access token, scope 'playlist-modify-private'
    :param name: string
    :param public: boolean
    :param collaborative: boolean
    :param description: string
    :return: a boolean indicating if it was created and a dict with the details
    """

    created = False

    query = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    body = {"name": str(name),
            "public": str(public),
            "collaborative": str(collaborative),
            "description": str(description)}

    response = requests.post(url=query, headers=headers, data=json.dumps(body))

    if response.status_code in (200, 201):
        created = True

    else:
        print(f"Error - Failed to create playlist {name} - Status code: {response.status_code}")

    details = None

    if created:
        details = response.json()

    return created, details


def add_song_to_playlist(playlist_id, access_token, song_uri, position):

    """
    Adds a song to the playlist specified by the playlist_id

    :param playlist_id: string
    :param access_token: string, required scope 'playlist-modify-private'
    :param song_uri: string
    :param position: integer
    :return: a boolean confirming addition and a dictionary with the details if successful
    """

    added = False

    query = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    query += f"?uris={song_uri}"
    query += f"&position={position}"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    response = requests.post(url=query, headers=headers)

    if response.status_code == 201:
        added = True

    details = None

    if added:
        details = response.json()

    return added, details


def read_csv_file(csv_filename, folder):
    """
    Reads a csv file into a DataFrame
    :param csv_filename: str
    :return: DataFrame
    """

    try:
        playlist_df = pd.read_csv(f"{folder}/{csv_filename}")
        playlist_df.drop(labels=["Unnamed: 0"], axis=1, inplace=True)
        return playlist_df

    except FileNotFoundError:
        print(f"\nError - Could not find the file: {csv_filename} in the folder {folder}")


def read_playlist_folder(folder):

    """
    Reads and combine all playlist csv files inside a folder into a DataFrame
    :param folder: str with the path i.e. ./playlists
    :return:
    """

    contents = os.listdir(folder)

    output_df = pd.DataFrame()

    for filename in contents:
        playlist_df = read_csv_file(filename, folder)
        output_df = pd.concat([output_df, playlist_df])

    output_df.reset_index(inplace=True)

    return output_df


def file_exists(filename, folder):

    return os.path.isfile(f"{folder}/{filename}")


def get_track_audio_features(track_id, access_token):
    """
    Retrieves the audio features of a track

    :param track_id: str with the unique id of the track
    :param access_token: str with a valid access token
    :return: a boolean indicating success, if it worked it returns a dict with the info
    """

    successful = False

    query = f"https://api.spotify.com/v1/audio-features/{track_id}"

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:
        print(f"Audio features of track: {track_id} requested successfully")
        successful = True
        output = response.json()

    else:
        print(f"Error: Request for audio features of track: {track_id} failed - Status code: {response.status_code}")
        output = None

    return successful, output


def get_album_info(album_id, access_token):
    """
    Retrieves the detailed info of an album

    :param album_id: str with the unique id of the album
    :param access_token: str with a valid access token
    :return: a boolean indicating success, if it worked it returns a dict with the info
    """

    successful = False

    query = f"https://api.spotify.com/v1/albums/{album_id}"

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:
        print(f"Detailed info of album: {album_id} requested successfully")
        successful = True
        output = response.json()

    else:
        print(f"Error: Request for album details: {album_id} failed - Status code: {response.status_code}")
        output = None

    return successful, output


def unpack_list_series(series):
    """

    Takes a Pandas Series in which each row has a lists of values
    i.e. row 1 = ['a','b']      row 2 = ['b','b']

    and returns another Pandas Series
    in which each individual value takes a row, also repeated values

    i.e. row 1 = ['a']      row 2 = ['b']     row 3 = ['b']      row 4 = ['b']

    :param series:
    :return: series
    """
    return pd.Series(sum(list(series.values), []))


def only_alphanumeric(string):

    """
    Strips all non alphanumeric characters from a string

    :param string: str with or without non alphanumeric chars
    :return: str with only alphanumeric chars
    """

    return re.sub(re.compile('\W'), '', string)


def load_playlist_from_input(playlist_folder):
    """

    Prompts the user to provide the name of a playlist
    keeps asking until it gets a valid playlist name
    that exists in the given folder

    Upon success it returns a tuple
    with the the playlist's and DataFrame

    :param playlist_folder: str
    :return: tuple(playlist_name, DataFrame of the playlist)
    """
    file_does_exist = False

    playlist_name = ""
    csv_filename = ""

    while not file_does_exist:
        playlist_name = input("\nType the name of the playlist:")
        csv_filename = f"{playlist_name}.csv"
        file_does_exist = file_exists(filename=csv_filename, folder=playlist_folder)
        if not file_does_exist:
            print("Wrong playlist name, try again")

    playlist_df = read_csv_file(csv_filename=csv_filename, folder=playlist_folder)

    return playlist_name, playlist_df
