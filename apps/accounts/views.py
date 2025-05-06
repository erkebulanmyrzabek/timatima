from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
import logging

from accounts.serializers import (
    CustomTokenObtainPairSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    WhatsAppUpdateSerializer
)

User = get_user_model()
logger = logging.getLogger('user_actions')

# Authentication views
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user_email = request.data.get('email', '')
            logger.info(f"User logged in: {user_email}")
        return response

class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"New user registered: {user.email}")
        
        return Response({
            'id': str(user.id),
            'email': user.email
        }, status=status.HTTP_201_CREATED)

# User profile views
class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"User updated profile: {user.email}")
        
        return Response({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })

class Update2FAView(generics.UpdateAPIView):
    serializer_class = WhatsAppUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"User updated 2FA number: {user.email}")
        
        return Response({
            'message': 'Updated'
        })

class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        email = user.email
        self.perform_destroy(user)
        
        logger.info(f"User deleted account: {email}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserByEmailView(APIView):
    """
    Поиск пользователя по email
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Не указан email'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            return Response({
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'middle_name': user.middle_name if hasattr(user, 'middle_name') else '',
            })
        except User.DoesNotExist:
            # Возвращаем пустой ответ вместо ошибки
            return Response(status=status.HTTP_204_NO_CONTENT) 