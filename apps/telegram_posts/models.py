import uuid
from django.db import models
from django.utils import timezone

class TelegramPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    media_url = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Пост из Telegram'
        verbose_name_plural = 'Посты из Telegram'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.title
