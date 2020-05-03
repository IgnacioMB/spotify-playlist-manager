"""
SCRIPT TO FIND OUT THE USERS TOP ARTISTS BY USER BEHAVIOR

"""

from spotify_functions import *

print("\nSelect the time range for the analysis:")

mod_selector = ""
time_range = None

while mod_selector not in ("l", "m", "s"):
    mod_selector = input("\nType (l) for long-term, (m) for medium-term or (s) for short-term:")
    if mod_selector not in ("l", "m", "s"):
        print("\nError selecting the time range for the analysis, invalid value given")

print(f"Input accepted. Your value given: {mod_selector}")

if mod_selector == "l":

    time_range = "long_term"

if mod_selector == "m":

    time_range = "medium_term"

if mod_selector == "s":

    time_range = "short_term"

# reading the credentials to read user name
spotify_credentials = read_jsonfile_as_dict("spotify_tokens.json")

if spotify_credential_check(required_scopes=None, credentials_dict=spotify_credentials):

    access_token = spotify_credentials["access_token"]
    refresh_token = spotify_credentials["refresh_token"]

    user_details = get_spotify_profile_details(access_token)

    playlist_df = get_user_top_artists(access_token=access_token, limit=10, offset=0, time_range=time_range)

    print(f"\nMost Listened Artists for Spotify user {user_details['display_name']} in {time_range}\n")

    print(playlist_df.to_string())

else:
    print("\nError - Credentials are not valid")
    sys.exit(1)
