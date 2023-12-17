import requests
import Tokens
from urllib.parse import urlencode
import base64
import webbrowser
import json

"""Class for handling calls to Spotify Api. 
Includes authentication & gathering latest music.
"""
class Spotify():

    def __init__(self):
      self.spotifyAuthCode = None
      self.spotifyAuthToken = None

    def getAuthCodeRoute(self):
        auth_headers = {
            "client_id": Tokens.CLIENT_ID,
            'client_secret': Tokens.CLIENT_SECRET,
            "response_type": "code",
            "redirect_uri": "http://127.0.0.1:5000/spotifyAuthenticate",
            "scope": "user-read-recently-played"
        }
        webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

    def setAuthCode(self, code):
      self.spotifyAuthCode = code

    def getAuthCode(self):
      return self.spotifyAuthCode

    def setAuthToken(self, token):
        self.spotifyAuthToken = token
    
    def getAuthToken(self):
        return self.spotifyAuthToken

    def getLatestMusic(self, code):
        encoded_credentials = base64.b64encode(Tokens.CLIENT_ID.encode() + b':' + Tokens.CLIENT_SECRET.encode()).decode("utf-8")

        token_headers = {
            "Authorization": "Basic " + encoded_credentials,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://127.0.0.1:5000/spotifyAuthenticate" #must be same redirect uri specified on dashboard
        }

        AUTH_URL = 'https://accounts.spotify.com/api/token'
        r = requests.post(AUTH_URL, data=token_data, headers=token_headers)
        
        if r.status_code != 200:
            return False

        # convert the response to JSON
        auth_response_data = r.json()

        # save the access token
        access_token = auth_response_data['access_token']

        self.setAuthToken(access_token)


        url = "https://api.spotify.com/v1/me/player/recently-played"
        response = requests.get(url, headers={"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer %s" % (access_token)})

        if response.status_code != 200: #maybe also want to check size of recent played here
            return False

        text_file = open("TestRecentMusic.json", "w")
        text_file.write(response.text)
        text_file.close()

        return response.json()["items"]