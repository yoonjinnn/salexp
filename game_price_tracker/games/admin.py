from django.contrib import admin
from .models import Game

# Register your models here.
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'game_name', 
        'maker', 
        'release_date',
        'original_price',
        'discount_price',
        'discount_startdate',
        'discount_enddate',
    )  # 목록에서 보여줄 필드

    list_filter = (
        'genre',
        'maker',
        'product_type',
        'game_language',
        'release_date',
    )  # 필터 사이드바

    search_fields = (
        'game_name',
        'maker',
        'genre',
    )  # 검색 기능

    ordering = ['-release_date']  # 기본 정렬 순서

    fieldsets = (
        ('게임 기본 정보', {
            'fields': (
                'game_name', 
                'genre', 
                'release_date', 
                'maker', 
                'product_type', 
                'player_number', 
                'game_language'
            )
        }),
        ('가격 및 할인 정보', {
            'fields': (
                'original_price', 
                'discount_price', 
                'discount_startdate', 
                'discount_enddate'
            )
        }),
        ('외부 링크', {
            'fields': (
                'game_image_url', 
                'game_url'
            )
        }),
    )
