from django.contrib import admin

# Register your models here.
from .models import User, Artist, Album, Song, Playlist_Song, Playlist

admin.site.register(User)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(Playlist_Song)
admin.site.register(Playlist)