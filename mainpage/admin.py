from django.contrib import admin
from .models import *

# Register your models here

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    fieldsets = [
        ('장르명', {'fields': ['genre_name']}),
    ]
    list_display = ('genre_name',)


class GenreInline(admin.TabularInline):
    model = Game.genre.through
    extra = 1


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    fieldsets = [
        ('언어명', {'fields': ['language']}),
    ]
    list_display = ('language',)


class LanguageInline(admin.TabularInline):
    model = Game.game_language.through
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    fieldsets = [
        ('게임명', {'fields': ['game_name']}),
        ('원가', {'fields': ['original_price']}),
        ('현재가격', {'fields': ['discount_price']}),
        ('개발사', {'fields': ['maker']}),
        ('발매일', {'fields': ['release_date']}),
        ('할인종료일', {'fields': ['discount_enddate']}),
    ]
    inlines = (GenreInline, LanguageInline,)
    list_display = ('get_title', 'original_price', 'discount_price', 'get_discount_percentage', 'get_genres', 'is_on_sale', 'get_discount_term', 'maker', 'get_languages')
    list_filter = ['maker', 'discount_enddate']
    search_fields = ['game_name']