from django.shortcuts import render
from .utils import get_spotify_client
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def home(request):
    sp = get_spotify_client()

    # Shows all of the attributes that sp can do
    # print(dir(sp))

    # Gets username
    user = sp.current_user()
    user = user["display_name"]

    if request.method == "POST":
        artist = request.POST["artist"]
        print(artist)

        # Fetch general data from Spotify (e.g., search for artists)
        results = sp.search(q=f'artist:{artist}', type='artist')
        artists = results['artists']['items']

        artist_id = artists[0]['id']
        print(sp.artist_top_tracks(artist_id))

        

        return render(request, 'musicapp/home.html', {
            'user': user,
            'artists': artists,
            })
    else:
        # sp = get_spotify_client()

        # Fetch general data from Spotify (e.g., search for artists)
        results = sp.search(q='artist:Coldplay', type='artist')
        artists = results['artists']['items']
        return render(request, 'musicapp/home.html', {
            'user': user,
            'artists': artists,
            })
