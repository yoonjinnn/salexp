from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Game, PriceHistory
from .serializers import GameSerializer, PriceHistorySerializer

# Create your views here.
class GameListCreateView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class GameRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class PriceHistoryView(APIView):
    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        histories = game.price_history.order_by('date')
        serializer = PriceHistorySerializer(histories, many=True)
        return Response(serializer.data)
