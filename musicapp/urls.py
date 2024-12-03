from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('spotify-login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.callback, name='callback'),
    path('logout/', views.logout_view, name='logout'),
    path('logout-confirmation/', views.logout_confirmation, name='logout_confirmation'),
    path('new_playlist/', views.create_playlist, name='create_playlist'),
    path('select-playlist/', views.select_playlist, name='select_playlist'),
    path('playlist/<str:playlist_id>/search-songs/', views.search_songs, name='search_songs'),
    path('playlist/<str:playlist_id>/add-songs/', views.add_song_to_playlist, name='add_song_to_playlist'),
    path('playlist/<str:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlist/<str:playlist_id>/delete_song/<str:song_id>/', views.delete_song_from_playlist, name='delete_song_from_playlist'),
    path('login/create-account', views.create_account, name='create_account'),
    path('login/returning-user', views.returning_user, name='returning_user'),
    path('analytics/', views.analytics, name='analytics'),
    path('playlist/<str:playlist_id>/analytics/', views.playlist_analytics, name='playlist_analytics'),
    path('quiz/<int:quiz_session_id>/summary/', views.quiz_summary, name='quiz_summary'),
    path('playlist/<str:playlist_id>/quiz/start/', views.start_quiz, name='start_quiz'),
    path('playlist/<str:playlist_id>/quiz/<int:question_index>/', views.quiz_question, name='quiz_question'),
    path('playlist/<str:playlist_id>/bulk-remove/artist/', views.bulk_remove_by_artist, name='bulk_remove_by_artist'),
    path('playlist/<str:playlist_id>/bulk-remove/album/', views.bulk_remove_by_album, name='bulk_remove_by_album'),
]
