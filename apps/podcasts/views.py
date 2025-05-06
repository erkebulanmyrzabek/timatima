from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from podcasts.models import Podcast
from podcasts.serializers import PodcastSerializer, PodcastListSerializer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from news.views import IsStaffOrReadOnly

# Настройка логирования
logger = logging.getLogger('user_actions')

class PodcastViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с подкастами"""
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lang', 'is_draft']
    search_fields = ['title', 'description']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']
    permission_classes = [IsStaffOrReadOnly]
    
    def get_queryset(self):
        """
        Если запрос от обычного пользователя - возвращаем только опубликованные подкасты.
        Для персонала - все подкасты.
        """
        queryset = Podcast.objects.all()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        # Для неавторизованных пользователей или не персонала - только опубликованные
        return queryset.filter(is_draft=False)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'list':
            return PodcastListSerializer
        return PodcastSerializer
    
    # Кэширование списка подкастов на 15 минут
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        logger.info(f"Подкаст создан пользователем {request.user.email}: {serializer.data.get('title')}")
        
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
        
        logger.info(f"Подкаст обновлен пользователем {request.user.email}: {instance.title}")
        
        return Response({
            'id': serializer.data.get('id'),
            'title': serializer.data.get('title')
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        self.perform_destroy(instance)
        
        logger.info(f"Подкаст удален пользователем {request.user.email}: {title}")
        
        return Response(status=status.HTTP_204_NO_CONTENT) 