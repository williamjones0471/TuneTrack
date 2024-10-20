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


from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.contrib.auth import logout

User = get_user_model()
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth import get_user_model
import spotipy
from spotipy.oauth2 import SpotifyOAuth

User = get_user_model()



"""
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
"""

def login_view(request):
    return render(request, 'musicapp/login.html')

    
def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='playlist-modify-private playlist-modify-public user-read-private user-read-email',
        cache_path=None
    )
    code = request.GET.get('code')

    try:
        token_info = sp_oauth.get_access_token(code)
    except Exception as e:
        # Handle the exception (e.g., log it and show an error message)
        print(f"Error obtaining access token: {e}")
        return render(request, 'musicapp/error.html', {'message': 'Failed to authenticate with Spotify.'})

    if token_info:
        # Ensure refresh_token is present
        if 'refresh_token' not in token_info:
            return render(request, 'musicapp/error.html', {'message': 'Failed to retrieve refresh token.'})

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

    """
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
"""
@login_required
def home(request):

    token_info = request.session.get('token_info', None)
    if not token_info:
        return redirect('login')
    
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='playlist-modify-private playlist-modify-public user-read-private user-read-email',
        cache_path=None,
    )

    
    
      # Check if token is expired
    if sp_oauth.is_token_expired(token_info):
        try:
            # Refresh the token
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            # Update the session with the new token_info
            request.session['token_info'] = token_info
        except Exception as e:
            print(f"Error refreshing access token: {e}")
            return redirect('login')

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Get the user's display name
        spotify_user = sp.current_user()
        user_display_name = spotify_user.get('display_name', 'User')
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return redirect('login')

    if request.method == "POST":
        artist = request.POST.get("artist", "")
        print(artist)

        try:
            # Fetch general data from Spotify (e.g., search for artists)
            results = sp.search(q=f'artist:{artist}', type='artist')
            artists = results['artists']['items']

            if artists:
                artist_id = artists[0]['id']
                top_tracks = sp.artist_top_tracks(artist_id)
                print(top_tracks)
        except Exception as e:
            print(f"Error searching for artist: {e}")
            artists = []
    else:
        try:
            # Fetch general data from Spotify (e.g., search for artists)
            results = sp.search(q='artist:Coldplay', type='artist')
            artists = results['artists']['items']
        except Exception as e:
            print(f"Error fetching default artist: {e}")
            artists = []

    return render(request, 'musicapp/home.html', {
        'user': user_display_name,
        'artists': artists,
    })

"""
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
"""
def logout_view(request):
    # Clear the session data
    request.session.flush()
    # Log out the user
    logout(request)
    return redirect('logout_confirmation')

def logout_confirmation(request):
    return render(request, 'musicapp/logout_confirmation.html')

def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='playlist-modify-private playlist-modify-public user-read-private user-read-email',
        cache_path=None
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def create_playlist(request):
       # Check if the user is authenticated and the access token exists
    token_info = request.session.get('token_info')
    
    if not token_info:
        # Redirect to the login page or Spotify auth flow if the token is missing
        return redirect('spotify_login')

    # Extract access token from session
    access_token = token_info.get('access_token')

    # Initialize the Spotipy client with the user's access token
    sp = spotipy.Spotify(auth=access_token)
    print("Token scopes:", token_info['scope'])

    if request.method == 'POST':
        print("Token scopes:", token_info['scope'])
        playlist_name = request.POST.get('playlist_name')
        playlist_description = request.POST.get('playlist_description')

        user_id = sp.current_user()['id']

        # Create a new playlist with the provided name and description
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,  # Set to False if you want the playlist to be private
            description=playlist_description
        )

        # After creating the playlist, you can redirect or display a success message
        return render(request, 'musicapp/playlist_success.html', {'playlist': playlist})

    return render(request, 'musicapp/create_playlist.html')