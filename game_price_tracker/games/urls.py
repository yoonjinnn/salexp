from django.urls import path
from .views import *

urlpatterns = [
    path('', get_game_list, name='game-list-create'),
    path('games/', GameListCreateView.as_view(), name='game-list'),
    path('games/<int:pk>/', GameRetrieveUpdateDestroyView.as_view(), name='game-detail'),
    path('games/<int:pk>/price-history', PriceHistoryView.as_view(), name='price-history'),
    path('genres/', GenreList.as_view(), name='genre-list'),
    path('languages/', LanguageList.as_view(), name='language-list'),
]
