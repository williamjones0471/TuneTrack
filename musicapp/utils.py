import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

def get_spotify_client():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=os.getenv('4461206ef25a4ebab77c254cdf61b2bc'),
        client_secret=os.getenv('SPO69401507e02f4b2fa968967ca7114f4f')
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp
