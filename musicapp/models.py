from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

# Create your models here.
# class User(AbstractUser):
#    pass

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='musicapp_user_set',
        related_query_name='musicapp_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='musicapp_user_permissions_set',
        related_query_name='musicapp_user_permission'
    )


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
    artist_id = models.ForeignKey(Artist, max_length=64, on_delete=models.CASCADE)
    album_id = models.ForeignKey(Album, max_length=64, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    duration = models.IntegerField(max_length=128)
    genre = models.CharField(max_length=64)

class Playlist_Song(models.Model):
    playlist_id = models.IntegerField(max_length=64, primary_key=True)
    playlist_song_id = models.IntegerField(max_length=64)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    date_added = models.DateTimeField(auto_now_add=True)

class Playlist(models.Model):
    playlist_id = models.IntegerField(max_length=64, primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    song_id = models.ManyToManyField(Playlist_Song)
    name = models.CharField(max_length=128, default='My Playlist')
    date_created = models.DateTimeField(auto_now_add=True)

