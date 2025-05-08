from django.contrib import admin
from .models import MailMessage, MailAttachment, PGPKey


@admin.register(MailAttachment)
class MailAttachmentAdmin(admin.ModelAdmin):
    """
    Админка для модели вложений
    """
    list_display = ['id', 'filename', 'file_size', 'content_type', 'created_at']
    search_fields = ['filename', 'content_type']
    readonly_fields = ['id', 'created_at']
    ordering = ('-created_at',)


@admin.register(MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    """
    Админка для модели сообщений
    """
    list_display = ['id', 'from_user', 'to_user', 'subject', 'is_encrypted', 'is_draft', 'created_at']
    list_filter = ['is_encrypted', 'is_draft', 'is_deleted_by_sender', 'is_deleted_by_recipient']
    search_fields = ['subject', 'from_user__email', 'to_user__email']
    readonly_fields = ['id', 'created_at']
    ordering = ('-created_at',)
    raw_id_fields = ('from_user', 'to_user')


@admin.register(PGPKey)
class PGPKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
