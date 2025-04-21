from django.urls import path, include
from .views import *

urlpatterns = [
    path('games/', GameList.as_view(), name='game-list'),

]