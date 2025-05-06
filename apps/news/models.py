import uuid
from django.db import models
from django.utils import timezone
from accounts.models import User

class News(models.Model):
    LANGUAGE_CHOICES = (
        ('kk', 'Қазақша'),
        ('ru', 'Русский'),
        ('en', 'English'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='news/images/')
    video_url = models.URLField(blank=True, null=True)
    lang = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')
    is_draft = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['lang']),
            models.Index(fields=['is_draft']),
            models.Index(fields=['published_at']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
