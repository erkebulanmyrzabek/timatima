import uuid
from django.db import models

class Localization(models.Model):
    LANGUAGE_CHOICES = (
        ('kk', 'Қазақша'),
        ('ru', 'Русский'),
        ('en', 'English'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lang = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    key = models.CharField(max_length=255)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'
        ordering = ['lang', 'key']
        indexes = [
            models.Index(fields=['lang']),
            models.Index(fields=['key']),
        ]
        unique_together = ('lang', 'key')
    
    def __str__(self):
        return f"{self.key} ({self.lang})"
