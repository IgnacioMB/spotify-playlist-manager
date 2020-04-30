"""
SCRIPT TO GENERATE A FILE WITH THE AUTHORIZATION TOKENS
NEEDED TO PROGRAMATICALLY READ/WRITE DATA CONCERNING YOUR SPOTIFY PLAYLISTS

NOTE: IT USES THE AUTHORIZATION CODE FLOW  TO ALLOW ACCESS TO USER RESOURCES
"""

import base64
from urllib.parse import urlencode
from spotify_functions import *

print("\nThis assistant generates a file with a temporary set of credentials to read or modify your Spotify playlists.")
print("It assumes you have registered your app and stored your client_id and client_secret in './secrets.json.'")
print("More info on: https://developer.spotify.com/documentation/general/guides/authorization-guide/")

spotify_secrets = read_jsonfile_as_dict("secrets.json")

spotify_clid = spotify_secrets["client_id"]
spotify_clsc = spotify_secrets["client_secret"]

redirect_uri = "https://example.com/callback/"

scope = "playlist-read-private playlist-modify-private"

# get the code
query = "https://accounts.spotify.com/authorize"
query += f"?client_id={spotify_clid}"
query += "&response_type=code"
query += f"&redirect_uri={redirect_uri}"
query += f"&scope={scope}"

response1 = requests.get(url=query)

if response1.status_code == 200:

    print("\nClick on the following link and copy the code param of the redirected url")
    print(response1.url)

    # copy the code in a variable
    code = input("\nPaste your code here:")

    # request refresh and access tokens
    query2 = "https://accounts.spotify.com/api/token"

    body = {"grant_type": "authorization_code", "code": code, "redirect_uri": "https://example.com/callback/"}

    body_url_encoded = urlencode(body)

    credentials_combo = f"{spotify_clid}:{spotify_clsc}"

    credentials_combo_base64 = base64.b64encode(credentials_combo.encode('ascii')).decode('ascii')

    headers = {"Authorization": f"Basic {credentials_combo_base64}",
               "Content-Type": "application/x-www-form-urlencoded"}

    response2 = requests.post(url=query2, data=body_url_encoded, headers=headers)

    if response2.status_code == 200:

        print("\nTokens retrieved successfully!")

        token_json = response2.json()

        creation_time = datetime.datetime.now()
        expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=token_json["expires_in"])

        token_json["creation_time"] = creation_time.strftime("%Y-%m-%d %H:%M:%S")
        token_json["expiration_time"] = expiration_time.strftime("%Y-%m-%d %H:%M:%S")

        with open("tokens.json", mode="w+") as token_fl:
            json.dump(token_json, token_fl)

        print("\nToken json exported to file './tokens.json'")
        print(f'\nDuration of the temporary credentials: {token_json["expires_in"]} seconds')
        print(f"Creation time of credentials: {creation_time}")
        print(f'Expiration time of credentials: {expiration_time}')

    else:

        print(f"\nError while requesting tokens - Status code: {response2.status_code}")

else:
    print(f'\nError while requesting authorization code - Status code:{response1.status_code}')
