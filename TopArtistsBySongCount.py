"""
SCRIPT TO FIND OUT THE USERS TOP ARTISTS BY SONG COUNT

You can choose to build the top considering:

-a single playlist
-all of the playlists within a folder (by default the user folder created during the playlist export)

It will show you the ranking on console and generate a bar plot

"""

from spotify_functions import *
import matplotlib.pyplot as plt

# reading the credentials to read user name
spotify_credentials = read_jsonfile_as_dict("tokens.json")

if credential_check(required_scopes=None, credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)

    user_id = user_details["id"]

    print("\nSelect the analysis modality")

    mod_selector = ""
    while mod_selector not in ("one", "all"):
        mod_selector = input("\nType (one) for analyzing a single playlist or (all) for analyzing all:")
        if mod_selector not in ("one", "all"):
            print("\nError selecting the analysis modality, invalid value given")

    print(f"Input accepted. Your value given: {mod_selector}")

    if mod_selector == "one":

        # read the playlist csv file
        playlist_name, playlist_df = load_playlist_from_input(playlist_folder=user_id)

    if mod_selector == "all":

        playlist_df = read_playlist_folder(folder=user_id)

    # the str field artists that contains the artist names for each song should be evaluated to a list
    playlist_df["artists"] = playlist_df["artists"].apply(lambda x: eval(x))

    # artist names might contain alphanumeric characters
    # that creates problems while generating visualizations
    # therefore we strip all non alphanumeric chars from them
    playlist_df["artists_stripped"] = playlist_df["artists"].apply(lambda my_list: [only_alphanumeric(item) for item in my_list])

    """
    ARTIST INSIGHTS
    """

    # calculate top 20 of most popular artists by song count in playlist
    unpacked_artist_series = unpack_list_series(playlist_df["artists_stripped"])

    artist_frequency_table = unpacked_artist_series.value_counts()

    top_20 = artist_frequency_table.head(20)

    print("\nTop 20 artists by song count in playlist\n")

    print(top_20.to_string())

    # analyze concentration of user liked songs per artist

    avg_songs_per_artist = artist_frequency_table.mean()
    print(f"\nAverage song count per artist: {avg_songs_per_artist}")

    # plot top 20 artist by song count in playlist as bar plot

    fig = plt.figure()

    axes = fig.add_axes([0.1, 0.4, 0.8, 0.5])

    axes.set_xlabel("Artist")
    axes.set_ylabel("Songs in playlist")
    axes.set_title(f"Top 20 Artists by song count")

    top_20.plot(kind="bar", axes=axes)

    plt.show()

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)
