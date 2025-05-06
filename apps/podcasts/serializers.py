from rest_framework import serializers
from podcasts.models import Podcast

class PodcastSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Podcast"""
    
    class Meta:
        model = Podcast
        fields = ['id', 'title', 'description', 'video_url', 
                 'image', 'is_draft', 'published_at', 'lang']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class PodcastListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка подкастов (облегченная версия)"""
    
    class Meta:
        model = Podcast
        fields = ['id', 'title', 'description', 'video_url', 
                 'image', 'published_at'] 