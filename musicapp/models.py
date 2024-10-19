from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    pass

class Artist(models.Model):
    artist_id = models.IntegerField(max_length=64, primary_key=True)
    name = models.CharField(max_length=128)
    genre = models.CharField(max_length=64)

class Album(models.Model):
    album_id = models.IntegerField(max_length=64, primary_key=True)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    release_date = models.DateField(max_length=64)

class Song(models.Model):
    song_id = models.IntegerField(max_length=64, primary_key=True)
    artist_id = models.ForeignKey(max_length=64, on_delete=models.CASCADE)
    album_id = models.ForeignKey(max_length=64, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    duration = models.IntegerField(max_length=128)
    genre = models.CharField(max_length=64)

class Playlist(models.Model):
    playlist_id = models.IntegerField(max_length=64, primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128),
    date_created = models.DateTimeField(auto_now_add=True)