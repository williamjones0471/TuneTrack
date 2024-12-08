from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
import json
import os
from django.shortcuts import get_object_or_404
import random


import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

from .models import User, QuizSession, Question, Playlist, Artist, Song, Playlist_Song, Playlist, Album

def login_view(request):
    cache.delete('login')
    return render(request, 'musicapp/login.html')

    
def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
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

            if user:
                return HttpResponseRedirect(reverse('returning_user'))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('create_account'))
        else:
            return render(request, 'musicapp/error.html', {'message': 'Failed to authenticate with Spotify.'})
    
def create_account(request):
    cache.delete('create_account')
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
    cache.delete('returning_user')
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
                'user': user_display_name,
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
        scope=settings.SPOTIFY_SCOPE,
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

    access_token = token_info.get('access_token')
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
    else:
        artists = []
        seed_artists = []
        seed_genres = []

        try:
            top_artists_data = sp.current_user_top_artists(limit=2, time_range='long_term')

            seed_artists = [items['id'] for items in top_artists_data['items']]

            for items in top_artists_data['items']:
                for genre in items['genres']:
                    if len(seed_genres) < 3:
                        seed_genres.append(genre)

            recommendations = sp.recommendations(limit=10, seed_artists=seed_artists, seed_genres=seed_genres)
            song_info = []
            artist_info = []

            print("\n\n", seed_artists, seed_genres, "\n\n")

            for recommendation in recommendations['tracks']:
                song_info.append(recommendation)
                artist_info.append(recommendation['album']['artists'][0])

        except Exception as e:
            print(f"Error fetching user's top artists or tracks: {e}")
            return render(request, "musicapp/home.html", {
                'user': user_display_name,
                # "message": "Unable to Get Recommendations.",
            })


        # zipped_data = zip(song_info, artist_info)

    return render(request, 'musicapp/home.html', {
        'user': user_display_name,
        'song_info': song_info,
        'artist_info': artist_info,
        'recommendations': recommendations['tracks']
    })

def logout_view(request):
    # Clear the session data
    cache.clear()
    request.session.flush()

    os.remove("/workspaces/TuneTrack/.cache")
    # Log out the user
    logout(request)
    return redirect('logout_confirmation')

def logout_confirmation(request):
    cache.clear()
    request.session.flush()
    return render(request, 'musicapp/logout_confirmation.html')

def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
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

    if request.method == 'POST':
        playlist_name = request.POST.get('playlist_name')
        playlist_description = request.POST.get('playlist_description')

        
        user_id = sp.current_user()['id']
        user = sp.current_user()['display_name']
        
        try:
            user = User.objects.get(username=user)
        except:
            return render(request, 'musicapp/create_playlist.html', {
                "message": "Playlist Creation Failed."
            })

        # Create a new playlist with the provided name and description
        try:
            playlist = sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=True,  # Set to False if you want the playlist to be private
                description=playlist_description
            )
        except:
            return render(request, 'musicapp/create_playlist.html', {
                "message": "Playlist Creation Failed."
            })

        playlist_id = playlist['id']

        user_id = sp.current_user()['id']
        user_display_name = sp.current_user()['display_name']
        user = User.objects.get(username=user_display_name)

        new_playlist = Playlist(owner=user, spotify_id=playlist_id, name=playlist['name'])
        new_playlist.save()

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
                        'duration': song['track']['duration_ms'] // 1000,
                        'image_url': song['track']['album']['images'][0]['url']
                    } for song in songs if song['track']
                ],
            }
        except Exception as e:
            print(f"Error fetching playlist details: {e}")
            return render(request, 'musicapp/error.html', {'message': 'Failed to fetch playlist details.'})
    
        return redirect('playlist_detail', playlist_id=playlist_id)

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
            except Exception as e:
                print(f"Error adding songs to playlist: {e}")
                return render(request, 'musicapp/error.html', {'message': 'Failed to add songs to playlist.'})
            
            user_id = sp.current_user()['id']
            user_display_name = sp.current_user()['display_name']
            user = User.objects.get(username=user_display_name)

            for song_id in song_ids:
                # print(song_ids)
                # if len(song_ids) < 2:
                #     song = sp.tracks(song_ids)
                #     print(song)
                # else:
                song = sp.tracks([song_id])
                print(song_id)

                artist_name = song['tracks'][0]['artists'][0]['name']
                artist_id = song['tracks'][0]['artists'][0]['id']

                uri = song['tracks'][0]['album']['uri']
                album_id = uri.split(":")[-1]
                album_name = song['tracks'][0]['album']['name']
                release_date = song['tracks'][0]['album']['release_date']

                song_name = song['tracks'][0]['name']
                duration = song['tracks'][0]['duration_ms'] // 1000
                release_date = song['tracks'][0]['album']['release_date']
                release_year = release_date.split("-")[0]

                try:
                    artist = Artist.objects.get(artist_id=artist_id)
                except ObjectDoesNotExist:
                    new_artist = Artist(artist_id=artist_id, name=artist_name)
                    new_artist.save()

                artist = Artist.objects.get(artist_id=artist_id)

                try: 
                    album = Album.objects.get(album_id=album_id)
                except ObjectDoesNotExist:
                    new_album = Album(album_id=album_id, artist_id=artist, title=album_name, release_date=release_date)
                    new_album.save()

                album = Album.objects.get(album_id=album_id)

                try:
                    song = Song.objects.get(song_id=song_id)
                except ObjectDoesNotExist:
                    new_song = Song(song_id=song_id, artist_id=artist, album_id=album, title=song_name, release_year=release_year, duration=duration)
                    new_song.save()

                try: 
                    playlist = Playlist.objects.get(spotify_id=playlist_id)
                    playlist_song = Playlist_Song.objects.get(song=song)
                except ObjectDoesNotExist:
                    new_playlist_song = Playlist_Song(playlist=playlist, song=song)
                    new_playlist_song.save()

            return redirect('search_songs', playlist_id=playlist_id) 

    return redirect('search_songs', playlist_id)

from django.shortcuts import render, redirect

def search_songs(request, playlist_id):
    token_info = request.session.get('token_info')
    
    if not token_info:
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)
    search_results = []

    try:
        playlist = sp.playlist(playlist_id)
        songs = playlist['tracks']['items']

        playlist_data = {
            'name': playlist['name'],
            'description': playlist.get('description', 'No description available.'),
            'songs': [
                {
                    'id': song['track']['id'],
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
        song_id = request.POST.get('song_id')
        song_name = request.POST.get('song_name')
        image_url = request.POST.get('image_url')
        song_duration = request.POST.get('song_duration')

        if song_id and song_name and image_url and song_duration:
            return redirect('playlist_detail', playlist_id=playlist_id, song_name=song_name, image_url=image_url, song_duration=song_duration)

        track_info = []

        if song_name:
            try:
                results = sp.search(q=song_name, type='track', limit=20)
                search_results = results.get('tracks', {}).get('items', [])

                for track in search_results:
                    track_data = {
                        'id': track['id'],
                        'name': track['name'],
                        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'artist': ", ".join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'] // 1000,
                    }
                    track_info.append(track_data)

                return render(request, 'musicapp/search_songs.html', {
                    'search_results': search_results, 
                    'playlist_id': playlist_id,  
                    'playlist': playlist_data,
                    'track_info': track_info
                })
            except Exception as e:
                print(f"Error processing search results: {e}")
        
    return render(request, 'musicapp/search_songs.html', {
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

    playlists = sp.current_user_playlists() 
    playlist_info = []

    try: 
        for playlist in playlists['items']:
            playlist_data = {
                'id': playlist['id'],
                'name': playlist['name'],
                'image_url': playlist['images'][0]['url'] if playlist['images'] else None,
            }
            playlist_info.append(playlist_data)
    except:
        pass
    

    return render(request, 'musicapp/select_playlist.html', {
        'playlist_info': playlist_info,
    })

def playlist_detail(request, playlist_id):
    token_info = request.session.get('token_info')

    if not token_info:
        # Redirect to the login page
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch playlist details from Spotify
        playlist = sp.playlist(playlist_id)
        songs = playlist['tracks']['items']

        # Prepare data for the template
        playlist_data = {
            'id': playlist_id,
            'name': playlist['name'],
            'description': playlist.get('description', 'No description available.'),
            'songs': [
                {
                    'id': song['track']['id'],
                    'title': song['track']['name'],
                    'artist_name': ', '.join([artist['name'] for artist in song['track']['artists']]),
                    'duration': song['track']['duration_ms'] // 1000,
                    'image_url': song['track']['album']['images'][0]['url'] if song['track']['album']['images'] else None  # Add image URL
                } for song in songs[::-1] if song['track']
            ],
        }
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        return render(request, 'musicapp/error.html', {'message': 'Failed to fetch playlist details.'})

    return render(request, 'musicapp/playlist_detail.html', {
        'playlist': playlist_data,
        'playlist_id': playlist_id,  # Pass the playlist ID explicitly
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

        song = Song.objects.get(song_id=song_id)

        try:
            playlist_song = Playlist_Song.objects.get(song=song)
            playlist_song.delete()
        except:
            pass

    except Exception as e:
        print(f"Error removing song: {e}")
        return render(request, 'musicapp/error.html', {'message': 'Failed to remove song from playlist.'})

    # Redirect back to the playlist detail page after successful deletion
    return redirect('playlist_detail', playlist_id=playlist_id)

@login_required
def analytics(request):
        # Get the access token from session
    token_info = request.session.get('token_info')

    if not token_info:
        return redirect('spotify_login')

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-top-read"
    )

    # Check and refresh token if necessary
    if sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            request.session['token_info'] = token_info
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return redirect('spotify_login')

    # Pass token to Spotipy
    sp = spotipy.Spotify(auth_manager=sp_oauth)


    # Fetch user's top artists and tracks
    try:
        top_artists_data = sp.current_user_top_artists(limit=50, time_range='long_term')
        top_tracks_data = sp.current_user_top_tracks(limit=50, time_range='long_term')
    except Exception as e:
        print(f"Error fetching user's top artists or tracks: {e}")
        return redirect('login')

    # Process genres
    genres = {}
    for artist in top_artists_data['items']:
        for genre in artist['genres']:
            genres[genre] = genres.get(genre, 0) + 1

    sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    top_genres = sorted_genres[:10]

    # Process mood/tempo analysis
    track_ids = [track['id'] for track in top_tracks_data['items']]


    #-------------------- FEATURE WAS DEPRECATED -----------------------------

    # try:
    #     audio_features = sp.audio_features(tracks=track_ids)
    # except spotipy.SpotifyException as e:
    #     return HttpResponseRedirect(reverse('home'))

    # tempo_list = [f['tempo'] for f in audio_features if f]
    # energy_list = [f['energy'] for f in audio_features if f]
    # valence_list = [f['valence'] for f in audio_features if f]

    # avg_tempo = sum(tempo_list) / len(tempo_list) if tempo_list else 0
    # avg_energy = sum(energy_list) / len(energy_list) if energy_list else 0
    # avg_valence = sum(valence_list) / len(valence_list) if valence_list else 0

    #-------------------------------------------------------------------------

    avg_tempo = random.uniform(30, 200)
    avg_energy = random.uniform(0,1)
    avg_valence = random.uniform(0,1)

    # Artist breakdown
    artist_counts = {}
    for track in top_tracks_data['items']:
        for artist in track['artists']:
            name = artist['name']
            artist_counts[name] = artist_counts.get(name, 0) + 1

    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    top_artists_breakdown = sorted_artists[:10]

    context = {
        'top_genres': top_genres,
        'avg_tempo': avg_tempo,
        'avg_energy': avg_energy,
        'avg_valence': avg_valence,
        'top_artists_breakdown': top_artists_breakdown,
    }

    return render(request, 'musicapp/analytics.html', context)

@login_required
def playlist_analytics(request, playlist_id):
    # Get the access token from session
    token_info = request.session.get('token_info')
    
    if not token_info:
        # Redirect to the login page 
        return redirect('spotify_login')

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=None
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
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    # Fetch playlist tracks
    try:
        playlist = sp.playlist(playlist_id)
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        messages.error(request, 'Failed to fetch playlist tracks.')
        return redirect('home')

    if not tracks:
        messages.info(request, 'No tracks found in the selected playlist.')
        return render(request, 'musicapp/playlist_analytics.html', {
            'playlist_name': playlist['name'],
            'playlist_id': playlist_id,
            'message': 'No tracks found in the selected playlist.',
        })

    # Process genres
    artist_ids = set()
    for item in tracks:
        if item['track'] and item['track']['artists']:
            for artist in item['track']['artists']:
                artist_ids.add(artist['id'])
    artist_ids = list(artist_ids)

    # Fetch artist genres in batches (max 50 per request)
    genres = {}
    for i in range(0, len(artist_ids), 50):
        batch_ids = artist_ids[i:i+50]
        artists_data = sp.artists(batch_ids)['artists']
        for artist in artists_data:
            for genre in artist['genres']:
                genres[genre] = genres.get(genre, 0) + 1

    sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    top_genres = sorted_genres[:10]

    # Process mood/tempo analysis
    track_ids = [item['track']['id'] for item in tracks if item['track'] and item['track']['id']]

    #-------------------- FEATURE WAS DEPRECATED -----------------------------

    # audio_features = []
    # for i in range(0, len(track_ids), 100):
    #     batch_ids = track_ids[i:i+100]
    #     audio_features.extend(sp.audio_features(batch_ids))

    # tempo_list = [f['tempo'] for f in audio_features if f]
    # energy_list = [f['energy'] for f in audio_features if f]
    # valence_list = [f['valence'] for f in audio_features if f]

    # avg_tempo = sum(tempo_list) / len(tempo_list) if tempo_list else 0
    # avg_energy = sum(energy_list) / len(energy_list) if energy_list else 0
    # avg_valence = sum(valence_list) / len(valence_list) if valence_list else 0

    #--------------------------------------------------------------------------

    avg_tempo = random.uniform(30, 200)
    avg_energy = random.uniform(0,1)
    avg_valence = random.uniform(0,1)

    # Artist breakdown
    artist_counts = {}
    for item in tracks:
        if item['track'] and item['track']['artists']:
            for artist in item['track']['artists']:
                name = artist['name']
                artist_counts[name] = artist_counts.get(name, 0) + 1

    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    top_artists_breakdown = sorted_artists[:10]

    context = {
        'playlist_name': playlist['name'],
        'playlist_id': playlist_id,
        'top_genres': top_genres,
        'avg_tempo': avg_tempo,
        'avg_energy': avg_energy,
        'avg_valence': avg_valence,
        'top_artists_breakdown': top_artists_breakdown,
    }

    return render(request, 'musicapp/playlist_analytics.html', context)

@login_required
def start_quiz(request, playlist_id):
    # Get access token from session
    token_info = request.session.get('token_info')
    if not token_info:
        return redirect('spotify_login')

    # Initialize Spotify client
    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch playlist details and track information
        playlist = sp.playlist(playlist_id)
        tracks = playlist['tracks']['items']

        if not tracks:
            messages.error(request, "No tracks found in this playlist to create a quiz.")
            return redirect('playlist_detail', playlist_id=playlist_id)

        # Process track data for the quiz
        quiz_data = []
        for item in tracks:
            track = item['track']
            quiz_data.append({
                'question': f"Guess the artist of the track: {track['name']}",
                'answer': track['artists'][0]['name'],
                'options': [track['artists'][0]['name'], "Artist 2", "Artist 3", "Artist 4"],  # Example options
            })

        # Store the quiz data in the session for use during the quiz
        request.session['quiz_data'] = quiz_data

        return redirect('quiz_question', playlist_id=playlist_id, question_index=0)

    except Exception as e:
        print(f"Error starting quiz: {e}")
        messages.error(request, "Failed to start the quiz.")
        return redirect('playlist_detail', playlist_id=playlist_id)

@login_required
def quiz_question(request, quiz_session_id, question_number):
    quiz_session = QuizSession.objects.get(id=quiz_session_id, user=request.user)
    
    if question_number > quiz_session.total_questions:
        return redirect('quiz_summary', quiz_session_id=quiz_session.id)
    
    if request.method == 'POST':
        # Process the user's answer
        selected_option = request.POST.get('option')
        question_id = request.POST.get('question_id')
        question = Question.objects.get(id=question_id)
        question.user_answer = selected_option
        question.is_correct = (selected_option == question.correct_answer)
        if question.is_correct:
            quiz_session.score += 1
        question.save()
        quiz_session.save()
        # Redirect to the next question
        return redirect('quiz_question', quiz_session_id=quiz_session.id, question_number=question_number + 1)
    else:
        # Generate or retrieve the question
        question = generate_question(quiz_session)
        context = {
            'quiz_session': quiz_session,
            'question': question,
            'question_number': question_number,
        }
        return render(request, 'musicapp/quiz_question.html', context)

@login_required
def quiz_summary(request, quiz_session_id):
    quiz_session = QuizSession.objects.get(id=quiz_session_id, user=request.user)
    questions = Question.objects.filter(quiz_session=quiz_session)
    context = {
        'quiz_session': quiz_session,
        'questions': questions,
    }
    return render(request, 'musicapp/quiz_summary.html', context)

def generate_question(quiz_session):
    # Check if a question already exists for this question number
    existing_questions = Question.objects.filter(quiz_session=quiz_session)
    if existing_questions.count() >= quiz_session.total_questions:
        return None  # All questions have been generated
    
    # Get songs from the playlist
    songs = Song.objects.filter(playlist=quiz_session.playlist)
    
    # Randomly select a song
    song = random.choice(songs)
    
    # Randomly choose a question type
    question_type = random.choice(['release_year', 'album_name', 'genre'])
    
    if question_type == 'release_year':
        question_text = f"In which year was '{song.title}' by {song.artist_name} released?"
        correct_answer = str(song.release_year)
        # Generate wrong options
        options = generate_year_options(correct_answer)
    elif question_type == 'album_name':
        question_text = f"Which album features the song '{song.title}' by {song.artist_name}?"
        correct_answer = song.album_name
        # Generate wrong options
        options = generate_album_options(correct_answer, song.artist_name)
    elif question_type == 'genre':
        question_text = f"What is the primary genre of '{song.title}' by {song.artist_name}?"
        correct_answer = song.genre
        # Generate wrong options
        options = generate_genre_options(correct_answer)
    else:
        # Fallback question
        question_text = f"Who is the artist of the song '{song.title}'?"
        correct_answer = song.artist_name
        options = generate_artist_options(correct_answer)
    
    # Save the question
    question = Question.objects.create(
        quiz_session=quiz_session,
        song=song,
        question_text=question_text,
        correct_answer=correct_answer
    )
    # Attach options to the question (in context for the template)
    question.options = options
    return question

def generate_year_options(correct_answer):
    correct_year = int(correct_answer)
    options = [correct_answer]
    while len(options) < 4:
        year = str(random.randint(correct_year - 5, correct_year + 5))
        if year not in options:
            options.append(year)
    random.shuffle(options)
    return options

def generate_album_options(correct_answer, artist_name):
    albums = Song.objects.filter(artist_name=artist_name).values_list('album_name', flat=True).distinct()
    albums = [album for album in albums if album != correct_answer]
    options = random.sample(albums, min(3, len(albums)))
    options.append(correct_answer)
    random.shuffle(options)
    return options

def generate_genre_options(correct_answer):
    genres = ['Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Classical', 'Electronic']
    genres = [genre for genre in genres if genre != correct_answer]
    options = random.sample(genres, 3)
    options.append(correct_answer)
    random.shuffle(options)
    return options

@login_required
def bulk_remove_by_artist(request, playlist_id):
    token_info = request.session.get('token_info')

    if not token_info:
        # Redirect to the login page
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch playlist details from Spotify
        playlist = sp.playlist(playlist_id)
        tracks = playlist['tracks']['items']

        if request.method == 'POST':
            artist_name = request.POST.get('artist_name')
            if artist_name:
                if artist_name != "":
                    # Get songs by the artist in the playlist
                    songs_to_remove = [
                        track for track in tracks
                        if any(artist['name'] == artist_name for artist in track['track']['artists'])
                    ]
                    track_uris = [track['track']['uri'] for track in songs_to_remove]

                    # Remove tracks from Spotify playlist
                    try:
                        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
                    except spotipy.exceptions.SpotifyException as e:
                        messages.error(request, f"An error occurred while removing songs: {e}")
                        return redirect('bulk_remove_by_artist', playlist_id=playlist_id)

                    messages.success(request, f"Successfully removed all songs by '{artist_name}' from the playlist.")
                    return redirect('playlist_detail', playlist_id=playlist_id)
                else:
                    return redirect('playlist_detail', playlist_id=playlist_id)
            else:
                return redirect('playlist_detail', playlist_id=playlist_id)
        else:
            # Get list of artists in the playlist
            artists = set(
                artist['name']
                for track in tracks if track['track']
                for artist in track['track']['artists']
            )
            context = {
                'playlist': {
                    'id': playlist_id,
                    'name': playlist['name'],
                },
                'artists': sorted(artists),
            }
            return render(request, 'musicapp/bulk_remove_by_artist.html', context)
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        messages.error(request, 'Failed to fetch playlist details.')
        return redirect('select_playlist')


@login_required
def bulk_remove_by_album(request, playlist_id):
    token_info = request.session.get('token_info')

    if not token_info:
        # Redirect to the login page
        return redirect('spotify_login')

    access_token = token_info.get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch playlist details from Spotify
        playlist = sp.playlist(playlist_id)
        tracks = playlist['tracks']['items']

        if request.method == 'POST':
            album_name = request.POST.get('album_name')
            if album_name:
                if album_name != "":
                    # Get songs from the album in the playlist
                    songs_to_remove = [
                        track for track in tracks
                        if track['track']['album']['name'] == album_name
                    ]
                    track_uris = [track['track']['uri'] for track in songs_to_remove]

                    # Remove tracks from Spotify playlist
                    try:
                        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
                    except spotipy.exceptions.SpotifyException as e:
                        messages.error(request, f"An error occurred while removing songs: {e}")
                        return redirect('bulk_remove_by_album', playlist_id=playlist_id)

                    messages.success(request, f"Successfully removed all songs from album '{album_name}' from the playlist.")
                    return redirect('playlist_detail', playlist_id=playlist_id)
                else:
                    return redirect('playlist_detail', playlist_id=playlist_id)
            else:
                return redirect('playlist_detail', playlist_id=playlist_id)
        else:
            # Get list of albums in the playlist
            albums = set(
                track['track']['album']['name']
                for track in tracks if track['track']
            )
            context = {
                'playlist': {
                    'id': playlist_id,
                    'name': playlist['name'],
                },
                'albums': sorted(albums),
            }
            return render(request, 'musicapp/bulk_remove_by_album.html', context)
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        messages.error(request, 'Failed to fetch playlist details.')
        return HttpResponseRedirect('select_playlist')