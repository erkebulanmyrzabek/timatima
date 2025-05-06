from django.contrib import admin
from .models import MailMessage, MailAttachment


class MailAttachmentAdmin(admin.ModelAdmin):
    """
    Админка для модели вложений
    """
    list_display = ['id', 'filename', 'file_size', 'content_type', 'created_at']
    search_fields = ['filename', 'content_type']
    readonly_fields = ['id', 'created_at']


class MailMessageAdmin(admin.ModelAdmin):
    """
    Админка для модели сообщений
    """
    list_display = ['id', 'from_user', 'to_user', 'subject', 'is_encrypted', 'is_draft', 'created_at']
    list_filter = ['is_encrypted', 'is_draft', 'is_deleted_by_sender', 'is_deleted_by_recipient']
    search_fields = ['from_user__email', 'to_user__email', 'subject']
    readonly_fields = ['id', 'created_at']


# Регистрируем модели в админке
admin.site.register(MailMessage, MailMessageAdmin)
admin.site.register(MailAttachment, MailAttachmentAdmin)
