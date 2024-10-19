"""
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
"""
"""
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def login_view(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope='user-read-private user-read-email',
        cache_path=None
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope='user-read-private user-read-email'
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        access_token = token_info['access_token']
        request.session['access_token'] = access_token

        # Fetch user profile information
        sp = spotipy.Spotify(auth=access_token)
        spotify_user = sp.current_user()

        # Create or get the user
        user, created = User.objects.get_or_create(
            username=spotify_user['id'],
            defaults={
                'email': spotify_user.get('email', ''),
                'first_name': spotify_user.get('display_name', '')
            }
        )
        auth_login(request, user)

        return redirect('home')
    else:
        return render(request, 'musicapp/error.html', {'message': 'Failed to authenticate with Spotify.'})

@login_required
def home(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-read-private user-read-email',
        cache_path=None,
    )

    token_info = sp_oauth.validate_token({'access_token': request.session.get('access_token')})

    if not token_info:
        # Token is invalid or expired, refresh it
        refresh_token = request.session.get('refresh_token')
        if refresh_token:
            token_info = sp_oauth.refresh_access_token(refresh_token)
            request.session['access_token'] = token_info['access_token']
            request.session['refresh_token'] = token_info['refresh_token']
        else:
            return redirect('login')

    sp = spotipy.Spotify(auth=request.session['access_token'])

    # Get the user's display name
    spotify_user = sp.current_user()
    user_display_name = spotify_user.get('display_name', 'User')

    if request.method == "POST":
        artist = request.POST.get("artist", "")
        print(artist)

        # Fetch general data from Spotify (e.g., search for artists)
        results = sp.search(q=f'artist:{artist}', type='artist')
        artists = results['artists']['items']

        if artists:
            artist_id = artists[0]['id']
            top_tracks = sp.artist_top_tracks(artist_id)
            print(top_tracks)

        return render(request, 'musicapp/home.html', {
            'user': user_display_name,
            'artists': artists,
        })
    else:
        # Fetch general data from Spotify (e.g., search for artists)
        results = sp.search(q='artist:Coldplay', type='artist')
        artists = results['artists']['items']
        return render(request, 'musicapp/home.html', {
            'user': user_display_name,
            'artists': artists,
        })

"""
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def login_view(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-read-private user-read-email',
        cache_path=None
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-read-private user-read-email',
        cache_path=None
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        # Store the entire token_info in the session
        request.session['token_info'] = token_info

        access_token = token_info['access_token']

        # Fetch user profile information
        sp = spotipy.Spotify(auth=access_token)
        spotify_user = sp.current_user()

        # Create or get the user
        user, created = User.objects.get_or_create(
            username=spotify_user['id'],
            defaults={
                'email': spotify_user.get('email', ''),
                'first_name': spotify_user.get('display_name', '')
            }
        )
        auth_login(request, user)

        return redirect('home')
    else:
        return render(request, 'musicapp/error.html', {'message': 'Failed to authenticate with Spotify.'})

@login_required
def home(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-read-private user-read-email',
        cache_path=None,
    )

    token_info = request.session.get('token_info', None)
    if not token_info:
        return redirect('login')

    # Check if token is expired
    if sp_oauth.is_token_expired(token_info):
        # Refresh the token
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        # Update the session with the new token_info
        request.session['token_info'] = token_info

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    # Get the user's display name
    spotify_user = sp.current_user()
    user_display_name = spotify_user.get('display_name', 'User')

    if request.method == "POST":
        artist = request.POST.get("artist", "")
        print(artist)

        # Fetch general data from Spotify (e.g., search for artists)
        results = sp.search(q=f'artist:{artist}', type='artist')
        artists = results['artists']['items']

        if artists:
            artist_id = artists[0]['id']
            top_tracks = sp.artist_top_tracks(artist_id)
            print(top_tracks)

        return render(request, 'musicapp/home.html', {
            'user': user_display_name,
            'artists': artists,
        })
    else:
        # Fetch general data from Spotify (e.g., search for artists)
        results = sp.search(q='artist:Coldplay', type='artist')
        artists = results['artists']['items']
        return render(request, 'musicapp/home.html', {
            'user': user_display_name,
            'artists': artists,
        })
