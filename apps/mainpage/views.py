from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from news.models import News
from podcasts.models import Podcast
from telegram_posts.models import TelegramPost
from lawyers.models import Lawyer
from news.serializers import NewsListSerializer
from podcasts.serializers import PodcastListSerializer
from telegram_posts.serializers import TelegramPostSerializer
from lawyers.serializers import LawyerListSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

# Create your views here.

logger = logging.getLogger('user_actions')

class MainPageNewsView(APIView):
    """API для получения новостей для главной страницы"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(cache_page(60 * 15))  # кэширование на 15 минут (восстановлено после исправления Redis)
    def get(self, request):
        """
        Получение списка новостей для главной страницы
        ?limit=5&lang=ru
        """
        limit = request.query_params.get('limit', 5)
        lang = request.query_params.get('lang', 'ru')
        
        news = News.objects.filter(
            is_draft=False, 
            lang=lang
        ).order_by('-published_at')[:int(limit)]
        
        serializer = NewsListSerializer(news, many=True)
        return Response({'news': serializer.data})

class MainPagePodcastsView(APIView):
    """API для получения подкастов для главной страницы"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(cache_page(60 * 15))  # кэширование на 15 минут (восстановлено после исправления Redis)
    def get(self, request):
        """
        Получение списка подкастов для главной страницы
        ?limit=3&lang=ru
        """
        limit = request.query_params.get('limit', 3)
        lang = request.query_params.get('lang', 'ru')
        
        podcasts = Podcast.objects.filter(
            is_draft=False,
            lang=lang
        ).order_by('-published_at')[:int(limit)]
        
        serializer = PodcastListSerializer(podcasts, many=True)
        return Response({'podcasts': serializer.data})

class MainPageTelegramPostsView(APIView):
    """API для получения телеграм постов для главной страницы"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(cache_page(60 * 15))  # кэширование на 15 минут (восстановлено после исправления Redis)
    def get(self, request):
        """
        Получение списка телеграм постов для главной страницы
        ?limit=5
        """
        limit = request.query_params.get('limit', 5)
        
        posts = TelegramPost.objects.all().order_by(
            '-published_at'
        )[:int(limit)]
        
        serializer = TelegramPostSerializer(posts, many=True)
        return Response({'posts': serializer.data})

class MainPageLawyersView(APIView):
    """API для получения адвокатов для главной страницы"""
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(cache_page(60 * 15))  # кэширование на 15 минут (восстановлено после исправления Redis)
    def get(self, request):
        """
        Получение списка адвокатов для главной страницы
        ?limit=6&is_featured=true
        """
        limit = request.query_params.get('limit', 6)
        is_featured = request.query_params.get('is_featured', 'true').lower() == 'true'
        
        lawyers = Lawyer.objects.filter(
            is_featured=is_featured
        ).order_by('-experience_years')[:int(limit)]
        
        serializer = LawyerListSerializer(lawyers, many=True)
        return Response({'lawyers': serializer.data})
