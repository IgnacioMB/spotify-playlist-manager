"""

PROJECT FUNCTIONS THAT RELATE TO THE YOUTUBE DATA API

"""

import requests
from utility_functions import *


def get_df_of_user_playlists(api_key, channel_id, max_results):
    """

    Retrieves a DataFrame with the YouTube channel's playlists
    (for now only a max of 'max_results', TO DO: PAGINATION)

    :param api_key: str with a valid api key to access Youtube Data API
    :param channel_id: str with the id of the channel
    :param max_results: int with the limit of results to obtain
    :return: a DataFrame with the channel lists
    """

    query = "https://www.googleapis.com/youtube/v3/playlists"
    query += f"?key={api_key}"
    query += "&part=snippet,contentDetails"
    query += f"&channelId={channel_id}"
    query += f"&maxResults={max_results}"

    headers = {'Accept': 'application/json'}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:

        user_pl_json = response.json()

        user_pl_df = pd.DataFrame(user_pl_json["items"])

        user_pl_df['title'] = user_pl_df['snippet'].apply(lambda x: x['title'])
        user_pl_df['description'] = user_pl_df['snippet'].apply(lambda x: x['description'])
        user_pl_df['publishedAt'] = user_pl_df['snippet'].apply(lambda x: x['publishedAt'])
        user_pl_df['itemCount'] = user_pl_df['contentDetails'].apply(lambda x: x['itemCount'])

        user_pl_df = user_pl_df[["id", "title", "itemCount", "publishedAt", "description", "etag"]]

        return user_pl_df

    else:
        print(f"\nError: Failed to request list of playlists from channel {channel_id} - Status Code: {response.status_code}")
        sys.exit(1)


def get_df_of_playlist_items(api_key, playlist_id):

    """

    Retrieves a DataFrame with the YouTube playlist items
    (for now only a max of 50, TO DO: PAGINATION)

    :param api_key: str with a valid api key to access Youtube Data API
    :param playlist_id: str with the id of the playlist
    :return: a DataFrame with the playlist items
    """

    query = "https://www.googleapis.com/youtube/v3/playlistItems"
    query += f"?key={api_key}"
    query += "&part=snippet,contentDetails"
    query += f"&playlistId={playlist_id}"
    query += f"&maxResults=50"

    headers = {'Accept': 'application/json'}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:

        user_pl_json = response.json()

        user_pl_df = pd.DataFrame(user_pl_json["items"])

        user_pl_df['title'] = user_pl_df['snippet'].apply(lambda x: x['title'])
        user_pl_df['description'] = user_pl_df['snippet'].apply(lambda x: x['description'])
        user_pl_df['addedAt'] = user_pl_df['snippet'].apply(lambda x: x['publishedAt'])
        user_pl_df['position'] = user_pl_df['snippet'].apply(lambda x: x['position'])
        user_pl_df['videoId'] = user_pl_df['contentDetails'].apply(lambda x: x['videoId'])
        user_pl_df['videoPublishedAt'] = user_pl_df['contentDetails'].apply(lambda x: x['videoPublishedAt'])

        user_pl_df = user_pl_df[["videoId", "title", "position", "addedAt", "description", "videoPublishedAt", "etag"]]

        return user_pl_df

    else:
        print(
            f"\nError: Failed to request items from playlist {playlist_id} - Status Code: {response.status_code}")
        sys.exit(1)


def get_video_category_id(api_key, videoId):

    """

    Retrieves the category id of the selected video

    :param api_key: str with a valid api key to access Youtube Data API
    :param videoId: str with the id of the video
    :return: a str with the category id of the video
    """

    query = "https://www.googleapis.com/youtube/v3/videos"
    query += f"?key={api_key}"
    query += "&part=snippet"
    query += f"&id={videoId}"

    headers = {'Accept': 'application/json'}

    response = requests.get(url=query, headers=headers)

    if response.status_code == 200:

        video_json = response.json()

        return video_json["items"][0]["snippet"]["categoryId"]

    else:
        print(
            f"\nError: Failed to request category id from video {videoId} - Status Code: {response.status_code}")
        sys.exit(1)