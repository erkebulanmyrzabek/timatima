import uuid
from django.db import models
from accounts.models import User

class Lawyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lawyer_profile')
    specialization = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField()
    about = models.TextField()
    languages = models.JSONField(default=list)  # Список языков, которыми владеет адвокат
    photo = models.ImageField(upload_to='lawyers/photos/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Адвокат'
        verbose_name_plural = 'Адвокаты'
        ordering = ['-experience_years']
        indexes = [
            models.Index(fields=['specialization']),
            models.Index(fields=['experience_years']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"
        
    @property
    def full_name(self):
        return self.user.get_full_name()
        
    @property
    def first_name(self):
        return self.user.first_name
        
    @property
    def last_name(self):
        return self.user.last_name
        
    @property
    def city(self):
        return self.user.city
