from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import spotipy
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from spotipy.oauth2 import SpotifyOAuth
from django.core.exceptions import ObjectDoesNotExist

from .models import User

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
        sp = spotipy.Spotify(auth=access_token)
        spotify_user = sp.current_user()
        user_display_name = spotify_user.get('display_name', 'User')

        try:
            user = User.objects.get(username=user_display_name)

            print(user, 'USERDSF:JKL')
            if user:
                return HttpResponseRedirect(reverse('returning_user'))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('create_account'))
        else:
            return render(request, 'musicapp/error.html', {'message': 'Failed to authenticate with Spotify.'})
    
def create_account(request):
    token_info = request.session.get('token_info')
    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)
    spotify_user = sp.current_user()
    user_display_name = spotify_user.get('display_name', 'User')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        password = request.POST['password']
        confirmation = request.POST['confirmation']

        if password != confirmation:
            return render(request, 'musicapp/create_account.html', {
                "message": "Passwords must match."
            })

        user = User.objects.create_user(username=spotify_user['display_name'], password=password, first_name=firstname, last_name=lastname, email=spotify_user.get('email'))
        user.save()

        user_auth = authenticate(request, username=user_display_name, password=password)
        print(user, user_auth)

        if user_auth is not None:
            login(request, user_auth)
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'musicapp/create_account.html', {
                "message": "Authentication Error"
            })
    
    return render(request, 'musicapp/create_account.html')

def returning_user(request):
    token_info = request.session.get('token_info')
    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)
    spotify_user = sp.current_user()
    user_display_name = spotify_user.get('display_name', 'User')

    if not token_info:
    #Redirect to the login page 
        return redirect('spotify_login')

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]


        try:
            user = User.objects.get(username=user_display_name)
        except ObjectDoesNotExist:
            return render(request, 'musicapp/create_account.html', {
                "message": "User does not exist."
            })
    
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'musicapp/returning_user.html', {
                "message": "Invalid username and/or password"
            })

    
    return render(request, 'musicapp/returning_user.html', {
                    'user': user_display_name
                })

@login_required
def home(request):
    token_info = request.session.get('token_info')

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
       #Check if user is authenticated and access token
    token_info = request.session.get('token_info')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    access_token = token_info.get('access_token')

    # Initialize the Spotipy client with the user access token
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

        # After creating the playlist display a success message
        return render(request, 'musicapp/playlist_success.html', {'playlist': playlist})

    return render(request, 'musicapp/create_playlist.html')

def add_song_to_playlist(request, playlist_id):
    # Get the access token from session
    token_info = request.session.get('token_info')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    if request.method == 'POST':
        song_ids = request.POST.getlist('song_ids')
        if song_ids:
            try:
                sp.playlist_add_items(playlist_id, song_ids)
                return redirect('search_songs', playlist_id=playlist_id)  
            except Exception as e:
                print(f"Error adding songs to playlist: {e}")
                return render(request, 'musicapp/error.html', {'message': 'Failed to add songs to playlist.'})

    return redirect('search_songs', playlist_id)

def search_songs(request, playlist_id):
    token_info = request.session.get('token_info')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)
    search_results = []

    try:
        # Fetch playlist details from Spotify
        playlist = sp.playlist(playlist_id)
        songs = playlist['tracks']['items']

        # Prepare data for the template
        playlist_data = {
            'name': playlist['name'],
            'description': playlist.get('description', 'No description available.'),
            'songs': [
                {
                    'id': song['track']['id'],  # Ensure we are including the song ID
                    'title': song['track']['name'],
                    'artist_name': ', '.join([artist['name'] for artist in song['track']['artists']]),
                    'duration': song['track']['duration_ms'] // 1000
                } for song in songs if song['track']
            ],
        }
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        return render(request, 'musicapp/error.html', {'message': 'Failed to fetch playlist details.'})

    if request.method == 'POST':
        song_name = request.POST.get('song_name')
        if song_name:
            # Perform the search
            results = sp.search(q=song_name, type='track', limit=10)
            search_results = results.get('tracks', {}).get('items', [])  # Access the list of tracks

    return render(request, 'musicapp/search_songs.html', {
        'search_results': search_results, 
        'playlist_id': playlist_id,  
        'playlist': playlist_data,
    })

def select_playlist(request):
    token_info = request.session.get('token_info')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    playlists = sp.current_user_playlists()  # Fetch user playlists

    return render(request, 'musicapp/select_playlist.html', {
        'playlists': playlists['items'],  # Pass playlists to the template
    })

def playlist_detail(request, playlist_id):
    token_info = request.session.get('token_info')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch playlist details from Spotify
        playlist = sp.playlist(playlist_id)
        songs = playlist['tracks']['items']

        # Prepare data for the template
        playlist_data = {
            'name': playlist['name'],
            'description': playlist.get('description', 'No description available.'),
            'songs': [
                {
                    'id': song['track']['id'],  # Ensure we are including the song ID
                    'title': song['track']['name'],
                    'artist_name': ', '.join([artist['name'] for artist in song['track']['artists']]),
                    'duration': song['track']['duration_ms'] // 1000
                } for song in songs if song['track']
            ],
        }
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        return render(request, 'musicapp/error.html', {'message': 'Failed to fetch playlist details.'})

    return render(request, 'musicapp/playlist_detail.html', {
        'playlist': playlist_data,
        'playlist_id': playlist_id  # Pass the playlist ID to the template
    })

def delete_song_from_playlist(request, playlist_id, song_id):
    token_info = request.session.get('token_info')
    
    if not token_info:
        #Redirect to the login page 
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    try:
        print(dir(sp))
        # Remove the song from the playlist using the Spotify API
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [song_id],)
    except Exception as e:
        print(f"Error removing song: {e}")
        return render(request, 'musicapp/error.html', {'message': 'Failed to remove song from playlist.'})

    # Redirect back to the playlist detail page after successful deletion
    return redirect('search_songs', playlist_id=playlist_id)