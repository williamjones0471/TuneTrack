from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('spotify-login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.callback, name='callback'),
    path('logout/', views.logout_view, name='logout'),
    path('logout-confirmation/', views.logout_confirmation, name='logout_confirmation'),

]
