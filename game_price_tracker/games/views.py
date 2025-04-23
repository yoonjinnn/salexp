from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from django.http import HttpResponseRedirect
import sqlite3
import datetime



def add_game(data):
    if not Game.objects.filter(game_name=data[0]):
        # Add data if data not exists
        if data[8] is None:
            if not Genre.objects.filter(genre_name='None'):
                Genre.objects.create(genre_name='None')
        else:
            for genre in data[8].replace(',', '').split():
                if not Genre.objects.filter(genre_name=genre):
                    Genre.objects.create(genre_name=genre)
        if data[12] is None:
            if not Language.objects.filter(language="None"):
                Language.objects.create(language="None")
        else:
            for lang in data[12].replace(',', '').split():
                if not Language.objects.filter(language=lang):
                    Language.objects.create(language=lang)
        # Add data to non-m2m fields
        game = Game.objects.create(
            game_name=data[0], 
            original_price=data[4],
            discount_price=data[5],
            maker=data[9],
            player_number=data[10],
            product_type=data[11],
            game_image_url=data[2],
            game_url=data[1],
            collect_date=data[13]
        )
        KST = datetime.timezone(datetime.timedelta(hours=9))
        if data[6] is not None:
            game.discount_startdate=datetime.datetime.strptime(data[6], '%Y-%m-%d %H:%M').replace(tzinfo=KST)
        if data[7] is not None:
            game.discount_enddate=datetime.datetime.strptime(data[7], '%Y-%m-%d %H:%M').replace(tzinfo=KST)
        if data[3] is not None:
            game.release_date=datetime.datetime.strptime(data[3], '%Y-%m-%d')
        # Add data to m2m fields
        if data[8] is not None:
            for g in data[8].replace(',', '').split():
                game.genre.add(Genre.objects.get(genre_name=g))
        else:
            game.genre.add(Genre.objects.get(genre_name='None'))
        if data[12] is not None:
            for l in data[12].replace(',', '').split():
                game.game_language.add(Language.objects.get(language=l))
        else:
            game.game_language.add(Language.objects.get(language='None'))

        game.save()
    return


def input_data():
    # DB 연결
    conn = sqlite3.connect("mainDB.db")
    cur = conn.cursor()

    # 데이터를 SELECT해서 확인
    cur.execute("SELECT * FROM game")  # games 테이블의 모든 데이터 조회
    rows = cur.fetchall()

    if len(rows) != Game.objects.all().count():
        for row in rows:
            add_game(row)

    # 연결 종료
    conn.close()
    return


def get_game_list(request):
    # initial setting - read DB if data not exists
    input_data()
    latest_game_list = Game.objects.order_by('-discount_enddate')
    context = {'games': latest_game_list}
    return HttpResponseRedirect('games')


# Create your views here.
class GameListCreateView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    def perform_create(self, serializer):
        serializer.save()

class GameRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class PriceHistoryView(APIView):
    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        histories = game.price_history.order_by('date')
        serializer = PriceHistorySerializer(histories, many=True)
        return Response(serializer.data)


class GenreList(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LanguageList(generics.ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer