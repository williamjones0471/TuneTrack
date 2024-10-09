from django.shortcuts import render
from .utils import get_spotify_client
import spotipy
from spotipy.oauth2 import SpotifyOAuth

spotify = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = '4461206ef25a4ebab77c254cdf61b2bc',
                                                      client_secret = '69401507e02f4b2fa968967ca7114f4f',
                                                      redirect_uri = 'http://localhost:8000/callback/'))

def home(request):
    sp = get_spotify_client()
    # Fetch general data from Spotify (e.g., search for artists)
    results = sp.search(q='artist:Coldplay', type='artist')
    artists = results['artists']['items']
    return render(request, 'musicapp/home.html', {'artists': artists})
