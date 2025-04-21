from django.shortcuts import render
from mainpage.models import *
from rest_framework import generics


# Create your views here.
class GameList(generics.ListCreateAPIView):
    gameset = Game.objects.all()
    
