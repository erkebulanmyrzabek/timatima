import uuid
from django.db import models
from django.utils import timezone

class Podcast(models.Model):
    LANGUAGE_CHOICES = (
        ('kk', 'Қазақша'),
        ('ru', 'Русский'),
        ('en', 'English'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    image = models.ImageField(upload_to='podcasts/images/')
    is_draft = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lang = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')
    
    class Meta:
        verbose_name = 'Подкаст'
        verbose_name_plural = 'Подкасты'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['lang']),
            models.Index(fields=['is_draft']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.title
