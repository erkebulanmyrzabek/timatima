from rest_framework import serializers
from news.models import News

class NewsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели News"""
    
    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'short_description', 'content', 
                 'image', 'video_url', 'lang', 'is_draft', 'published_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        
class NewsCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания новости"""
    
    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'short_description', 'content', 
                 'image', 'video_url', 'lang', 'is_draft', 'published_at']
    
    def create(self, validated_data):
        # Добавляем пользователя, создавшего новость
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class NewsListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка новостей (облегченная версия)"""
    
    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'short_description', 'image', 
                 'video_url', 'published_at'] 