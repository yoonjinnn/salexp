from rest_framework import serializers
from mainpage.models import *
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueTogetherValidator


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['genre_name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ['language']


class GameSerializer(serializers.ModelSerializer):
    genre = serializers.StringRelatedField(many=True, read_only=True)
    game_language = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Game
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "두 패스워드가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        # User 내에 username의 중복확인 코드가 들어가 있음
        model = User
        fields = ['username', 'password', 'password2']


class UserSerializer(serializers.ModelSerializer):
    # questions = serializers.SlugRelatedField(many=True, read_only=True, slug_field='pub_date')
    questions = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='question-detail')

    class Meta:
        model = User
        fields = ['id', 'username', 'questions']
