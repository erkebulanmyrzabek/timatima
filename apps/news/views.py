from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from news.models import News
from news.serializers import NewsSerializer, NewsCreateSerializer, NewsListSerializer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

# Настройка логирования
logger = logging.getLogger('user_actions')

# Пользовательское разрешение для проверки прав на создание/редактирование контента
class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет только персоналу создавать/редактировать/удалять,
    а остальным только просматривать.
    """
    def has_permission(self, request, view):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Запись разрешена только персоналу
        return request.user and request.user.is_staff

class NewsViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с новостями"""
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lang', 'is_draft']
    search_fields = ['title', 'content', 'short_description']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']
    permission_classes = [IsStaffOrReadOnly]
    
    def get_queryset(self):
        """
        Если запрос от обычного пользователя - возвращаем только опубликованные новости.
        Для персонала - все новости.
        """
        queryset = News.objects.all()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        # Для неавторизованных пользователей или не персонала - только опубликованные
        return queryset.filter(is_draft=False)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return NewsCreateSerializer
        elif self.action == 'list':
            return NewsListSerializer
        return NewsSerializer
    
    # Кэширование списка новостей на 15 минут (восстановлено после исправления Redis)
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        logger.info(f"Новость создана пользователем {request.user.email}: {serializer.data.get('title')}")
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'id': serializer.data.get('id'),
            'title': serializer.data.get('title'),
            'slug': serializer.data.get('slug')
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Новость обновлена пользователем {request.user.email}: {instance.title}")
        
        return Response({
            'id': serializer.data.get('id'),
            'title': serializer.data.get('title'),
            'slug': serializer.data.get('slug')
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        self.perform_destroy(instance)
        
        logger.info(f"Новость удалена пользователем {request.user.email}: {title}")
        
        return Response(status=status.HTTP_204_NO_CONTENT) 