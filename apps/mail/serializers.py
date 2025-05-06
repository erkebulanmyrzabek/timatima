from rest_framework import serializers
from mail.models import MailMessage, MailAttachment
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class UserEmailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения пользователя в списке сообщений
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'middle_name']


class MailAttachmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели MailAttachment
    """
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MailAttachment
        fields = ['id', 'filename', 'file_size', 'content_type', 'file_url', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_file_url(self, obj):
        """
        Получаем URL для доступа к файлу
        """
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None


class MailMessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели MailMessage
    """
    from_user = UserEmailSerializer(read_only=True)
    to_user = UserEmailSerializer(read_only=True)
    to_user_id = serializers.CharField(write_only=True)
    attachments = MailAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = MailMessage
        fields = [
            'id', 'from_user', 'to_user', 'to_user_id', 'subject', 
            'content_encrypted', 'attachments', 'attachments_meta', 'is_encrypted',
            'is_draft', 'created_at'
        ]
        read_only_fields = ['id', 'from_user', 'created_at']
    
    def validate_to_user_id(self, value):
        """
        Проверка валидности UUID для to_user_id
        Если начинается с 'temp-', это временный ID для нового пользователя
        """
        if value.startswith('temp-'):
            return value
            
        try:
            return str(uuid.UUID(value))
        except ValueError:
            raise serializers.ValidationError("Must be a valid UUID.")
    
    def create(self, validated_data):
        # Устанавливаем отправителя как текущего пользователя
        validated_data['from_user'] = self.context['request'].user
        
        # Находим получателя по ID
        to_user_id = validated_data.pop('to_user_id')
        
        # Если ID начинается с 'temp-', это временный ID
        if to_user_id.startswith('temp-'):
            # Используем текущего пользователя как временного получателя
            validated_data['to_user'] = self.context['request'].user
        else:
            try:
                to_user = User.objects.get(id=to_user_id)
                validated_data['to_user'] = to_user
            except User.DoesNotExist:
                # Используем текущего пользователя как получателя,
                # чтобы избежать ошибки валидации
                validated_data['to_user'] = self.context['request'].user
        
        return super().create(validated_data)


class MailMessageListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка сообщений
    """
    from_user = UserEmailSerializer(read_only=True)
    to_user = UserEmailSerializer(read_only=True)
    has_attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = MailMessage
        fields = ['id', 'from_user', 'to_user', 'subject', 'is_encrypted', 'is_draft', 'created_at', 'has_attachments']
    
    def get_has_attachments(self, obj):
        """
        Проверяем, есть ли у сообщения вложения
        """
        # Проверяем наличие вложений через связь ManyToMany
        has_attachments = obj.attachments.exists()
        
        # Также проверяем attachments_meta (JSON поле)
        has_attachments_meta = bool(obj.attachments_meta and len(obj.attachments_meta) > 0)
        
        # Добавляем отладочную информацию
        print(f"Сообщение {obj.id}: has_attachments={has_attachments}, has_attachments_meta={has_attachments_meta}, количество вложений={obj.attachments.count()}")
        
        if not has_attachments and has_attachments_meta:
            # Автоматически восстанавливаем связи для вложений, если они есть в meta
            for attachment_data in obj.attachments_meta:
                attachment_id = attachment_data.get('id')
                if attachment_id:
                    try:
                        attachment = MailAttachment.objects.get(id=attachment_id)
                        obj.attachments.add(attachment)
                        has_attachments = True
                        print(f"Восстановлена связь с вложением: {attachment_id}")
                    except MailAttachment.DoesNotExist:
                        print(f"Вложение не найдено: {attachment_id}")
                    except Exception as e:
                        print(f"Ошибка при обработке вложения: {e}")
        
        # Если есть любые вложения, возвращаем True
        return has_attachments or has_attachments_meta


class MailAttachmentUploadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для загрузки вложений
    """
    file = serializers.FileField(required=True)
    
    class Meta:
        model = MailAttachment
        fields = ['file']
    
    def create(self, validated_data):
        file_obj = validated_data['file']
        
        # Создаем новое вложение
        attachment = MailAttachment(
            file=file_obj,
            filename=file_obj.name,
            file_size=file_obj.size,
            content_type=file_obj.content_type or 'application/octet-stream'
        )
        attachment.save()
        
        return attachment 