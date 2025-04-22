from django.urls import path, include
from .views import *


urlpatterns = [
    path('games/', GameList.as_view(), name='main app page'),
    path('games/<int:pk>', GameDetail.as_view(), name='game-detail'),
    path('genres/', GenreList.as_view(), name='genre-list'),
    path('languages/', LanguageList.as_view(), name='language-list'),
    path('api-auth/', include("rest_framework.urls")),
    path('register/', RegisterUser.as_view()),
    path('users/', UserList.as_view(), name='user-list'),
]