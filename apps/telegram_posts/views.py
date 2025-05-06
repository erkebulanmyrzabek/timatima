from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from telegram_posts.models import TelegramPost
from telegram_posts.serializers import TelegramPostSerializer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from news.views import IsStaffOrReadOnly

# Create your views here.

logger = logging.getLogger('user_actions')

class TelegramPostViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с постами из Telegram"""
    queryset = TelegramPost.objects.all().order_by('-published_at')
    serializer_class = TelegramPostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']
    permission_classes = [IsStaffOrReadOnly]
    
    # Кэширование списка постов на 15 минут
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        logger.info(f"Telegram пост создан пользователем {request.user.email}: {serializer.data.get('title')}")
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'id': serializer.data.get('id'),
            'title': serializer.data.get('title')
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Telegram пост обновлен пользователем {request.user.email}: {instance.title}")
        
        return Response({
            'id': serializer.data.get('id'),
            'title': serializer.data.get('title')
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        self.perform_destroy(instance)
        
        logger.info(f"Telegram пост удален пользователем {request.user.email}: {title}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
