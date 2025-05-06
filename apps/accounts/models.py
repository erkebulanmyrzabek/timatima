import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    def get_short_name(self):
        return self.first_name
