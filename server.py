import serial
import requests
import spotipy
import re

# CHANGE ME
port = "/dev/ttyACM4"
SPOTIPY_CLIENT_ID = "<client_id>"
SPOTIPY_CLIENT_SECRET = "<client_secret>"
SPOTIPY_REDIRECT_URI = "http://localhost:33232/callback"
# You have to set up a redirect URI in your Spotify Developer Dashboard


button = 0
button_state = False
pot = 0
pot_state = False


def spotify_current_song(token) -> str:
    url = "http://api.spotify.com/v1/me/player/currently-playing"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 204:
        return "No song playing"
    if response.status_code == 200:
        return response.json()["item"]["name"] + " " * 16
    return "" * 16


def spotify_setup() -> str:
    scope = "user-read-currently-playing user-modify-playback-state user-read-playback-state user-read-private"
    sp_oauth = spotipy.SpotifyOAuth(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope
    )
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        print("No token found, click following link to authorize")
        print(sp_oauth.get_authorize_url())
        sp_oauth.get_authorize_url()
        response = input("Enter the URL you were redirected to: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
        return token_info["access_token"]
    if sp_oauth.is_token_expired(token_info):
        print("Token expired")
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    print("Token found")
    return token_info["access_token"]


def spotify_control(token, data):
    global button
    global pot
    global button_state
    global pot_state
    try:
        if not data:
            return
        regex_button = r"b=(\d+)"
        regex_pot = r"p=(\d+)"

        if rex_result := re.search(regex_button, data):
            button = int(rex_result.group(1))
        if rex_result := re.search(regex_pot, data):
            pot = int(rex_result.group(1))

        # compare states if changed, change pot only if 15% difference

        if button_state != button:
            button_state = button
            if button_state:
                requests.put(
                    "http://api.spotify.com/v1/me/player/play",
                    headers={"Authorization": f"Bearer {token}"},
                )
            else:
                requests.put(
                    "http://api.spotify.com/v1/me/player/pause",
                    headers={"Authorization": f"Bearer {token}"},
                )
        if abs(pot - pot_state) > 15:
            pot_state = pot
            requests.put(
                f"http://api.spotify.com/v1/me/player/volume?volume_percent={pot}",
                headers={"Authorization": f"Bearer {token}"},
            )
    except Exception as e:
        print(e)
        pass


def main():
    bearer = spotify_setup()
    current_song = ""
    with serial.Serial(port, 9600, timeout=1) as ser:
        while True:
            ser.write(b".\r\n")  # Send heartbeat
            data = ser.readline().decode()
            print(data)
            if data:
                spotify_control(bearer, data)
            new_song = spotify_current_song(bearer)
            if current_song != new_song:
                current_song = new_song
                print(new_song)
                song_name = "$" + new_song[:16] + "\r\n"
                ser.write(song_name.encode())


if __name__ == "__main__":
    main()
