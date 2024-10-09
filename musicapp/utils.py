import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

# Load environment variables
load_dotenv()

def get_spotify_client():
<<<<<<< HEAD
    # client_credentials_manager = SpotifyClientCredentials(
    #     client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    #     client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')

    #     #Spotify client id = 4461206ef25a4ebab77c254cdf61b2bc
    #     #Spotify client secret = SPO69401507e02f4b2fa968967ca7114f4f
    # )
    # sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = '4461206ef25a4ebab77c254cdf61b2bc', 
                                                     client_secret = 'SPO69401507e02f4b2fa968967ca7114f4f', 
                                                     redirect_uri = 'http://localhost:8080'))
    return sp
=======
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp
>>>>>>> refs/remotes/origin/main
