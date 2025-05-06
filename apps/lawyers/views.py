from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from lawyers.models import Lawyer
from lawyers.serializers import LawyerSerializer, LawyerListSerializer, LawyerCreateSerializer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from news.views import IsStaffOrReadOnly

# Create your views here.

logger = logging.getLogger('user_actions')

class LawyerViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с адвокатами"""
    queryset = Lawyer.objects.all()
    serializer_class = LawyerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'experience_years', 'is_featured']
    search_fields = ['user__first_name', 'user__last_name', 'specialization', 'about']
    ordering_fields = ['experience_years', 'user__last_name']
    ordering = ['-experience_years']
    permission_classes = [IsStaffOrReadOnly]
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'list':
            return LawyerListSerializer
        elif self.action == 'create':
            return LawyerCreateSerializer
        return LawyerSerializer
    
    # Кэширование списка адвокатов на 15 минут
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lawyer = self.perform_create(serializer)
        
        # Получаем данные о пользователе
        user = lawyer.user
        logger.info(f"Адвокат создан пользователем {request.user.email}: {user.first_name} {user.last_name}")
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'id': serializer.data.get('id'),
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        return serializer.save()
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        user = instance.user
        logger.info(f"Адвокат обновлен пользователем {request.user.email}: {user.first_name} {user.last_name}")
        
        return Response({
            'id': serializer.data.get('id'),
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        name = f"{user.first_name} {user.last_name}"
        self.perform_destroy(instance)
        
        logger.info(f"Адвокат удален пользователем {request.user.email}: {name}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
