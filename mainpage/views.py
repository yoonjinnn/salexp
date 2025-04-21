from django.shortcuts import render
from .models import *
from django.shortcuts import get_object_or_404
import sqlite3
from django.http import HttpResponse


def input_data():
    # DB 연결
    conn = sqlite3.connect("mainDB.db")
    cur = conn.cursor()

    # 데이터를 SELECT해서 확인
    cur.execute("SELECT * FROM game")  # game 테이블의 모든 데이터 조회
    rows = cur.fetchall()

    for row in rows:
        # Add data if data not exists
        for genre in row[6].replace(',', '').split():
            if not Genre.objects.filter(genre_name=genre):
                Genre.objects.create(genre_name=genre)
        for lang in row[11].replace(',', '').split():
            if not Language.objects.filter(language=lang):
                Language.objects.create(language=lang)

        # Add data to non-m2m fields
        game = Game.objects.create(
            id=row[0],
            game_name=row[1], 
            original_price=row[2], 
            discount_price=row[3],
            discount_startdate=row[4],
            discount_enddate=row[5],
            release_date=row[7],
            maker=row[8],
            player_number=row[9],
            product_type=row[10],
            game_image_url=row[12],
            game_url=row[13]
        )
        
        # Add data to m2m fields
        for g in row[6].replace(',', '').split():
            game.genre.add(Genre.objects.get(genre_name=g))
        for l in row[11].replace(',', '').split():
            game.game_language.add(Language.objects.get(language=l))
        game.save()

    # 연결 종료
    conn.close()
    return


def get_game_list(request):
    # initial setting - read DB if data not exists
    games = Game.objects.first()
    if not games:
        input_data()

    latest_game_list = Game.objects.order_by('discount_enddate')
    context = {'games': latest_game_list}
    return render(request, 'sites/gamelist.html', context)


def get_game_detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'sites/detail.html', {'game':game.__dict__})

