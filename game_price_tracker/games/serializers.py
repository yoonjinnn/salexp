from rest_framework import serializers
from .models import *

class GameSerializer(serializers.ModelSerializer):
    genre = serializers.StringRelatedField(many=True, read_only=True)
    game_language = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Game
        fields = '__all__'

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        field = ['date', 'price']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['language']
