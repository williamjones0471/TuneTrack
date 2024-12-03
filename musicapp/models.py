from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User
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
    artist_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    genre = models.CharField(max_length=255, null=False, default="Unknown")

class Album(models.Model):
    album_id = models.IntegerField(primary_key=True)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    release_date = models.DateField(max_length=64)

class Song(models.Model):
    song_id = models.IntegerField(primary_key=True)
    artist_id = models.ForeignKey(Artist, max_length=64, on_delete=models.CASCADE)
    album_id = models.ForeignKey(Album, max_length=64, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    release_year = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField()
    genre = models.CharField(max_length=255, null=False, default="Unknown")
    

    def __str__(self):
        return f"{self.title} by {self.artist_name}"

class Playlist_Song(models.Model):
    playlist = models.ForeignKey('Playlist', on_delete=models.CASCADE) 
    song = models.ForeignKey(Song, on_delete=models.CASCADE)           
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'song')

class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=128, default='My Playlist')
    date_created = models.DateTimeField(auto_now_add=True)
    songs = models.ManyToManyField('Song', through='Playlist_Song', blank=True)

    def __str__(self):
        return self.name



class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    user_answer = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(null=True)

