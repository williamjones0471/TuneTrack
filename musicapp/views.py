from django.shortcuts import render
from .utils import get_spotify_client
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def home(request):
    sp = get_spotify_client()
    # Fetch general data from Spotify (e.g., search for artists)
    results = sp.search(q='artist:Coldplay', type='artist')
    artists = results['artists']['items']
    return render(request, 'musicapp/home.html', {'artists': artists})
