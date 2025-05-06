from rest_framework import serializers
from telegram_posts.models import TelegramPost

class TelegramPostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TelegramPost"""
    
    class Meta:
        model = TelegramPost
        fields = ['id', 'title', 'content', 'media_url', 'published_at']
        read_only_fields = ['id', 'created_at', 'updated_at'] 