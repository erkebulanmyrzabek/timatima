from rest_framework import serializers
from localization.models import Localization

class LocalizationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Localization"""
    
    class Meta:
        model = Localization
        fields = ['id', 'lang', 'key', 'value']
        read_only_fields = ['id', 'created_at', 'updated_at']

class LocalizationByLangSerializer(serializers.ModelSerializer):
    """Сериализатор для переводов по языку (без ID и lang)"""
    
    class Meta:
        model = Localization
        fields = ['key', 'value'] 