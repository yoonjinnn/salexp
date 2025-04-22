from django.shortcuts import render
from mainpage.models import *
from rest_framework import generics
from .serializers import *
from rest_framework import generics
from .permissions import *

# Create your views here.
class GameList(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAdminOrReadOnly]
    def perform_create(self, serializer):
        serializer.save()


class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAdminOrReadOnly]


class GenreList(generics.ListAPIView):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer


class LanguageList(generics.ListAPIView):
    queryset = Languages.objects.all()
    serializer_class = LanguageSerializer


class RegisterUser(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
