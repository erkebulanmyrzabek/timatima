from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

from accounts.serializers import (
    AdminUserSerializer,
    AdminUserCreateSerializer
)

User = get_user_model()
logger = logging.getLogger('user_actions')

class AdminUserListCreateView(generics.ListCreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']
    
    def get_queryset(self):
        queryset = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateSerializer
        return AdminUserSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'users': serializer.data,
                'total': queryset.count()
            })
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'users': serializer.data,
            'total': queryset.count()
        })
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        logger.info(f"Admin user created by {request.user.email}: {user.email}")
        
        return Response({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_201_CREATED)

class AdminUserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Admin user updated by {request.user.email}: {instance.email}")
        
        return Response({
            'id': str(instance.id),
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        email = instance.email
        self.perform_destroy(instance)
        
        logger.info(f"Admin user deleted by {request.user.email}: {email}")
        
        return Response(status=status.HTTP_204_NO_CONTENT) 