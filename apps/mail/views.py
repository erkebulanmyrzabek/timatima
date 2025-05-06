from rest_framework import viewsets, permissions, status, filters, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from mail.models import MailMessage, MailAttachment
from mail.serializers import (
    MailMessageSerializer, MailMessageListSerializer, 
    MailAttachmentSerializer, MailAttachmentUploadSerializer
)
from django.db import models, transaction


class MailAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с вложениями писем
    """
    queryset = MailAttachment.objects.all()
    serializer_class = MailAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Добавляем поддержку загрузки файлов через FormData
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    def get_serializer_class(self):
        """
        Использовать разные сериализаторы для списка и деталей
        """
        if self.action == 'create' or self.action == 'upload_multiple':
            return MailAttachmentUploadSerializer
        return MailAttachmentSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Создание нового вложения (загрузка файла)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save()
        
        # Возвращаем данные о загруженном файле
        return Response(
            MailAttachmentSerializer(attachment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def upload_multiple(self, request):
        """
        Эндпоинт для загрузки нескольких файлов одним запросом
        """
        files = request.FILES.getlist('files')
        
        if not files:
            return Response(
                {"error": "Файлы не предоставлены"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachments = []
        with transaction.atomic():
            for file_obj in files:
                serializer = MailAttachmentUploadSerializer(data={'file': file_obj})
                serializer.is_valid(raise_exception=True)
                attachment = serializer.save()
                attachments.append(attachment)
        
        # Возвращаем данные о загруженных файлах
        return Response(
            MailAttachmentSerializer(
                attachments, many=True, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Удаление вложения
        """
        instance = self.get_object()
        
        # Проверяем, что файл не используется в сообщениях
        if instance.messages.exists():
            return Response(
                {"error": "Невозможно удалить файл, т.к. он используется в сообщениях"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Удаляем файл и запись в БД
        instance.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class MailViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления почтовыми сообщениями
    """
    serializer_class = MailMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает сообщения в зависимости от типа запроса (входящие/исходящие/черновики/корзина)
        """
        user = self.request.user
        
        # Проверяем, является ли действие получением отдельного элемента
        if self.action == 'retrieve':
            # Для получения отдельного сообщения используем простой фильтр без union()
            return MailMessage.objects.filter(
                models.Q(from_user=user) | models.Q(to_user=user)
            )
        
        # Определяем базовый queryset для текущего действия
        if self.action == 'inbox':
            # Входящие сообщения: получатель - текущий пользователь, не черновик, не в корзине
            return MailMessage.objects.filter(
                to_user=user, 
                is_draft=False,
                is_deleted_by_recipient=False
            )
        elif self.action == 'sent':
            # Отправленные: отправитель - текущий пользователь, не черновик, не в корзине
            return MailMessage.objects.filter(
                from_user=user, 
                is_draft=False,
                is_deleted_by_sender=False
            )
        elif self.action == 'drafts':
            # Черновики: отправитель - текущий пользователь, черновик, не в корзине
            return MailMessage.objects.filter(
                from_user=user, 
                is_draft=True,
                is_deleted_by_sender=False
            )
        elif self.action == 'trash':
            # Корзина: сообщения, удаленные пользователем (отправленные или полученные)
            sent_deleted = MailMessage.objects.filter(
                from_user=user, 
                is_deleted_by_sender=True
            )
            received_deleted = MailMessage.objects.filter(
                to_user=user, 
                is_deleted_by_recipient=True
            )
            return sent_deleted.union(received_deleted)
        else:
            # По умолчанию: все сообщения, связанные с пользователем
            sent = MailMessage.objects.filter(from_user=user)
            received = MailMessage.objects.filter(to_user=user)
            return sent.union(received)

    def get_serializer_class(self):
        """
        Использовать разные сериализаторы для списка и деталей
        """
        if self.action in ['list', 'inbox', 'sent', 'drafts', 'trash']:
            return MailMessageListSerializer
        return MailMessageSerializer

    def perform_create(self, serializer):
        """
        Автоматически установить отправителя как текущего пользователя
        """
        message = serializer.save(from_user=self.request.user)
        
        # Обработка вложений, если они были переданы
        attachments_meta = serializer.validated_data.get('attachments_meta', [])
        if attachments_meta:
            print(f"Обрабатываем вложения для сообщения {message.id}: {attachments_meta}")
            
            # Прикрепляем вложения к сообщению по их ID, если они существуют
            for attachment_data in attachments_meta:
                attachment_id = attachment_data.get('id')
                if attachment_id:
                    try:
                        attachment = MailAttachment.objects.get(id=attachment_id)
                        message.attachments.add(attachment)
                        print(f"Вложение {attachment_id} успешно прикреплено к сообщению {message.id}")
                    except MailAttachment.DoesNotExist:
                        print(f"Вложение с ID {attachment_id} не найдено")
                    except Exception as e:
                        print(f"Ошибка при прикреплении вложения {attachment_id}: {str(e)}")
                else:
                    print(f"Отсутствует ID вложения в данных: {attachment_data}")
            
            # Проверяем количество прикрепленных вложений после добавления
            attachments_count = message.attachments.count()
            print(f"Количество прикрепленных вложений после обработки: {attachments_count}")
            
            # Сохраняем изменения в сообщении
            message.save()
    
    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """
        Эндпоинт для получения входящих писем
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        # Возвращаем просто список сообщений, без обертки
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """
        Эндпоинт для получения отправленных писем
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        # Возвращаем просто список сообщений, без обертки
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def drafts(self, request):
        """
        Эндпоинт для получения черновиков
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        # Возвращаем просто список сообщений, без обертки
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trash(self, request):
        """
        Эндпоинт для получения удаленных писем
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        # Возвращаем просто список сообщений, без обертки
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Перемещение сообщения в корзину, а не полное удаление
        """
        message = self.get_object()
        user = request.user
        
        # Помечаем сообщение как удаленное для текущего пользователя
        if message.from_user.id == user.id:
            message.is_deleted_by_sender = True
            message.save()
        elif message.to_user.id == user.id:
            message.is_deleted_by_recipient = True
            message.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Восстановление сообщения из корзины
        """
        message = self.get_object()
        user = request.user
        
        # Восстанавливаем сообщение для текущего пользователя
        if message.from_user.id == user.id:
            message.is_deleted_by_sender = False
            message.save()
        elif message.to_user.id == user.id:
            message.is_deleted_by_recipient = False
            message.save()
        
        return Response({"message": "Сообщение восстановлено"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def permanent_delete(self, request, pk=None):
        """
        Полное удаление сообщения (только если оно в корзине)
        """
        message = self.get_object()
        user = request.user
        
        # Проверяем, находится ли сообщение в корзине
        if (message.from_user.id == user.id and message.is_deleted_by_sender) or \
           (message.to_user.id == user.id and message.is_deleted_by_recipient):
            # Если удалено и отправителем и получателем, или одно из них не существует
            if (message.is_deleted_by_sender and message.is_deleted_by_recipient) or \
               (message.is_deleted_by_sender and not message.to_user) or \
               (message.is_deleted_by_recipient and not message.from_user):
                # Удаляем сообщение полностью
                message.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(
            {"error": "Сообщение не может быть полностью удалено"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Получение отдельного сообщения с подробной информацией о вложениях
        """
        instance = self.get_object()
        
        # Логируем информацию о вложениях для отладки
        print(f"ID сообщения: {instance.id}")
        print(f"Число вложений (attachments): {instance.attachments.count()}")
        print(f"Вложения (attachments_meta): {instance.attachments_meta}")
        
        # Загружаем связанные вложения, если они есть
        if not instance.attachments.exists() and instance.attachments_meta:
            # Если у сообщения есть мета-информация о вложениях, но нет связей с моделями MailAttachment
            # Попробуем восстановить связи по ID в attachments_meta
            for attachment_data in instance.attachments_meta:
                attachment_id = attachment_data.get('id')
                if attachment_id:
                    try:
                        attachment = MailAttachment.objects.get(id=attachment_id)
                        instance.attachments.add(attachment)
                        print(f"Восстановлена связь с вложением: {attachment_id}")
                    except MailAttachment.DoesNotExist:
                        print(f"Вложение не найдено: {attachment_id}")
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data) 