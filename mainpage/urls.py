from django.urls import path
from . import views

app_name = 'salexp'
urlpatterns = [
    path("", views.get_game_list, name='game-list'),
    path('<int:game_id>/', views.get_game_detail, name='game-detail'),
]