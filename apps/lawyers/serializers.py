from rest_framework import serializers
from lawyers.models import Lawyer
from accounts.models import User

class LawyerSerializer(serializers.ModelSerializer):
    """Полный сериализатор для модели Lawyer"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    city = serializers.CharField(source='user.city', read_only=True)
    
    class Meta:
        model = Lawyer
        fields = ['id', 'user', 'first_name', 'last_name', 'city', 'specialization', 
                  'experience_years', 'about', 'languages', 'photo', 'is_featured']
        read_only_fields = ['id', 'created_at', 'updated_at']

class LawyerListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка адвокатов"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    city = serializers.CharField(source='user.city', read_only=True)
    
    class Meta:
        model = Lawyer
        fields = ['id', 'first_name', 'last_name', 'specialization', 
                  'experience_years', 'about', 'languages', 'photo', 'city']

class LawyerCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания записи об адвокате"""
    
    class Meta:
        model = Lawyer
        fields = ['id', 'user', 'specialization', 'experience_years', 'about', 
                  'languages', 'photo', 'is_featured'] 