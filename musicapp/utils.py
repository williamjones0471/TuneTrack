import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

# Load environment variables
load_dotenv()

def get_spotify_client():
    # sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = '4461206ef25a4ebab77c254cdf61b2bc', 
    #                                                  client_secret = 'SPO69401507e02f4b2fa968967ca7114f4f', 
    #                                                  redirect_uri = 'http://localhost:8080/callback/'))

    sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = 'f1675f5f0d9c4f43b99b5eab4e381ab0', 
                                                     client_secret = '2b464e065bb64a7887edee8f40bb9391', 
                                                     redirect_uri = 'http://localhost:8080/callback/'))
    return sp