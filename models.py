from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import datetime


# Create your models here.
class GenreTag(models.Model):
    genre_name = models.CharField(default='', verbose_name='장르명', max_length=50)
    
    def __str__(self):
        return self.genre_name


class Language(models.Model):
    language = models.CharField(default='', verbose_name='언어', max_length=50)

    def __str__(self):
        return self.language


class Game(models.Model):
    game_name = models.CharField(verbose_name='게임명', max_length=50)
    original_price = models.IntegerField(verbose_name='원가', default=0)
    discount_price = models.IntegerField(verbose_name='현재가격', default=0)
    discount_startdate = models.DateTimeField(blank=True, default=timezone.now(), verbose_name='할인시작일')
    discount_enddate = models.DateTimeField(blank=True, verbose_name='할인종료일')
    genre = models.ManyToManyField('GenreTag', default='', blank=True, through='GameGenreTag', verbose_name='장르')
    release_date = models.DateTimeField(blank=True, verbose_name='발매일')
    maker = models.CharField(verbose_name='개발사', max_length=100)
    player_number = models.IntegerField(verbose_name='플레이 인원수', default=1)
    product_type = models.BooleanField(verbose_name='상품유형(실물여부)', default=False)
    game_language = models.ManyToManyField('Language', through='GameLanguage', default='', verbose_name='대응언어')
    game_image_url = models.URLField(max_length=200, default='', verbose_name='이미지URL')
    game_url = models.URLField(max_length=100, default='', verbose_name='URL')
    
    @admin.display(description='장르')
    def get_genres(self):
        return ", ".join([g.genre_name for g in self.genre.all()])

    @admin.display(description='지원언어')
    def get_languages(self):
        return ", ".join([l.language for l in self.game_language.all()])
    
    @admin.display(description='종료까지')
    def get_discount_term(self):
        if self.discount_enddate >= timezone.now():
            return f'D-{(self.discount_enddate.date() - timezone.now().date()).days}'
        else:
            return f'-'

    @admin.display(description='할인율')
    def get_discount_percentage(self):
        if self.original_price != 0:
            return f'{round((1 - (self.discount_price / self.original_price)) * 100, 2)}%'
        else:
            return None

    @admin.display(boolean=True, description='종료임박(7일기준)')
    def ends_soon(self):
        return datetime.timedelta(days=7) >= self.discount_enddate - timezone.now()

    @admin.display(boolean=True, description='할인중')
    def is_on_sale(self):
        return (self.original_price > self.discount_price) & (self.get_discount_term() != '-')
    
    @admin.display(boolean=True, description='최근생성(3일기준)')
    def was_published_recently(self):
        return self.release_date >= timezone.now() - datetime.timedelta(days=3)

    def get_title(self):
        last_badge, sale_badge, new_badge = "", "", ""
        if self.is_on_sale():
            sale_badge = "<Sale>"
            if self.ends_soon():
                last_badge = "<Last!!>"
        if self.was_published_recently():
            new_badge = "<New>"
        return f'{last_badge}{sale_badge}{new_badge} {self.game_name}'


# ManyToManyField에 의해 사용될 중간 테이블 - 태그별 조회 시 사용
class GameGenreTag(models.Model):
    class Meta:
        db_table = 'game_genretag'
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    genretag = models.ForeignKey('GenreTag', on_delete=models.CASCADE)
    

class GameLanguage(models.Model):
    class Meta:
        db_table = 'game_language'
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    language = models.ForeignKey('Language', on_delete=models.CASCADE)