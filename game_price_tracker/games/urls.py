from django.urls import path
from .views import GameListCreateView, GameRetrieveUpdateDestroyView, PriceHistoryView


urlpatterns = [
    path('', GameListCreateView.as_view(), name='game-list-create'),
    path('<int:pk>/', GameRetrieveUpdateDestroyView.as_view(), name='game-detail'),
    path('<int:pk>/price-history', PriceHistoryView.as_view(), name='price-history'),
]
