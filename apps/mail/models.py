from django.db import models
import uuid
import os
from django.conf import settings


def get_attachment_file_path(instance, filename):
    """
    Функция для определения пути сохранения файла вложения
    """
    # Создаем уникальное имя файла с использованием UUID
    unique_filename = f"{uuid.uuid4()}-{filename}"
    # Возвращаем путь: media/mail_attachments/UUID-имя_файла
    return os.path.join('mail_attachments', unique_filename)


class MailAttachment(models.Model):
    """
    Модель для хранения вложений сообщений
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=get_attachment_file_path, verbose_name="Файл")
    filename = models.CharField(max_length=255, verbose_name="Имя файла")
    file_size = models.PositiveIntegerField(verbose_name="Размер файла (байт)")
    content_type = models.CharField(max_length=100, verbose_name="Тип содержимого")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} ({self.file_size} байт)"
    
    def delete(self, *args, **kwargs):
        """
        Переопределяем метод delete, чтобы удалить сам файл при удалении записи
        """
        # Проверяем существование файла и удаляем его
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)


class MailMessage(models.Model):
    """
    Модель для хранения почтовых сообщений между пользователями системы
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="Отправитель"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name="Получатель"
    )
    subject = models.CharField(max_length=255, verbose_name="Тема")
    content_encrypted = models.TextField(verbose_name="Зашифрованное содержимое")
    attachments = models.ManyToManyField(MailAttachment, blank=True, related_name="messages", verbose_name="Вложения")
    attachments_meta = models.JSONField(default=list, blank=True, verbose_name="Метаданные вложений")
    is_encrypted = models.BooleanField(default=True, verbose_name="Зашифровано")
    is_draft = models.BooleanField(default=False, verbose_name="Черновик")
    is_deleted_by_sender = models.BooleanField(default=False, verbose_name="Удалено отправителем")
    is_deleted_by_recipient = models.BooleanField(default=False, verbose_name="Удалено получателем")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"От: {self.from_user.email} К: {self.to_user.email} - {self.subject}"
        
    def is_in_trash(self, user):
        """
        Проверяет, находится ли сообщение в корзине для указанного пользователя
        """
        if user.id == self.from_user.id:
            return self.is_deleted_by_sender
        elif user.id == self.to_user.id:
            return self.is_deleted_by_recipient
        return False 
    
