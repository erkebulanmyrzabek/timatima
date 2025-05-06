from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from localization.models import Localization
from localization.serializers import LocalizationSerializer, LocalizationByLangSerializer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from news.views import IsStaffOrReadOnly

# Create your views here.

logger = logging.getLogger('user_actions')

class LocalizationViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с локализацией"""
    queryset = Localization.objects.all()
    serializer_class = LocalizationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['lang']
    search_fields = ['key', 'value']
    permission_classes = [IsStaffOrReadOnly]
    
    # Кэширование списка переводов на 1 час
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Кэширование переводов по языку на 1 час
    @method_decorator(cache_page(60 * 60))
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='by-lang')
    def by_lang(self, request):
        """Получение переводов по языку"""
        lang = request.query_params.get('lang', 'ru')
        translations = Localization.objects.filter(lang=lang)
        serializer = LocalizationByLangSerializer(translations, many=True)
        return Response({'translations': serializer.data})
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        logger.info(f"Перевод создан пользователем {request.user.email}: {serializer.data.get('key')} ({serializer.data.get('lang')})")
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'id': serializer.data.get('id'),
            'lang': serializer.data.get('lang'),
            'key': serializer.data.get('key')
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Перевод обновлен пользователем {request.user.email}: {instance.key} ({instance.lang})")
        
        return Response({
            'id': serializer.data.get('id'),
            'lang': serializer.data.get('lang'),
            'key': serializer.data.get('key')
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        key_info = f"{instance.key} ({instance.lang})"
        self.perform_destroy(instance)
        
        logger.info(f"Перевод удален пользователем {request.user.email}: {key_info}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
