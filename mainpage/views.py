from django.shortcuts import render
from .models import *
from django.shortcuts import get_object_or_404
import sqlite3
from django.http import HttpResponse
import datetime
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm


def add_game(data):
    # Add data if data not exists
    for genre in data[7].replace(',', '').split():
        if not Genre.objects.filter(genre_name=genre):
            Genre.objects.create(genre_name=genre)
    for lang in data[12].replace(',', '').split():
        if not Language.objects.filter(language=lang):
            Language.objects.create(language=lang)

    if not Game.objects.filter(game_name=data[1]):
        # Add data to non-m2m fields
        game = Game.objects.create(
            game_name=data[1], 
            original_price=int(data[3].replace('₩', '').replace(',', '')), 
            discount_price=int(data[4].replace('₩', '').replace(',', '')),
            maker=data[9],
            player_number=data[10],
            product_type=data[11],
            game_image_url=data[2],
            game_url=data[0],
            collect_date=data[13]
        )
        if data[5] is not None:
            game.discount_startdate=datetime.datetime.strptime(data[5], '%Y/%m/%d %H:%M')
        if data[6] is not None:
            game.discount_enddate=datetime.datetime.strptime(data[6], '%Y/%m/%d %H:%M')
        if data[8] is not None:
            game.release_date=datetime.datetime.strptime(data[8], '%y.%m.%d')
        # Add data to m2m fields
        for g in data[7].replace(',', '').split():
            game.genre.add(Genre.objects.get(genre_name=g))
        for l in data[12].replace(',', '').split():
            game.game_language.add(Language.objects.get(language=l))
        game.save()
    return


def input_data():
    # DB 연결
    conn = sqlite3.connect("mainDB.db")
    cur = conn.cursor()

    # 데이터를 SELECT해서 확인
    cur.execute("SELECT * FROM game")  # game 테이블의 모든 데이터 조회
    rows = cur.fetchall()

    for row in rows:
        add_game(row)

    # 연결 종료
    conn.close()
    return


def get_game_list(request):
    # initial setting - read DB if data not exists
    if not Game.objects.first():
        input_data()
    latest_game_list = Game.objects.order_by('-discount_enddate')
    context = {'games': latest_game_list}
    return render(request, 'sites/gamelist.html', context)


def get_game_detail(request, game_id):
    # initial setting - read DB if data not exists
    if not Game.objects.first():
        input_data()
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'sites/detail.html', {'game':game.__dict__})


class SignupView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('user-list')
    template_name = 'sites/signup.html'