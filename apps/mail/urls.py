from django.urls import path, include
from rest_framework.routers import DefaultRouter
from mail.views import MailViewSet, MailAttachmentViewSet, PGPKeyViewSet

# Создаем маршрутизатор для API
router = DefaultRouter()
router.register(r'pgp-keys', PGPKeyViewSet, basename='pgp-key')
router.register(r'', MailViewSet, basename='mail')
router.register(r'attachments', MailAttachmentViewSet, basename='mail-attachment')


# Определяем URL-маршруты для приложения
urlpatterns = [
    # Добавляем все маршруты из роутера
    path('', include(router.urls)),
    
    # Также добавляем прямые пути к специальным действиям
    path('inbox/', MailViewSet.as_view({'get': 'inbox'}), name='mail-inbox'),
    path('sent/', MailViewSet.as_view({'get': 'sent'}), name='mail-sent'),
    path('drafts/', MailViewSet.as_view({'get': 'drafts'}), name='mail-drafts'),
    path('trash/', MailViewSet.as_view({'get': 'trash'}), name='mail-trash'),
    
    # Пути для PGP-ключей
    path('pgp-keys/my_keys/', PGPKeyViewSet.as_view({'get': 'my_keys'}), name='pgp-key-my-keys'),
    path('pgp-keys/public_key/', PGPKeyViewSet.as_view({'get': 'public_key'}), name='pgp-key-public'),
    
    # Новые маршруты для управления сессией PGP
    path('pgp-keys/create_session/', PGPKeyViewSet.as_view({'post': 'create_session'}), name='pgp-key-create-session'),
    path('pgp-keys/end_session/', PGPKeyViewSet.as_view({'post': 'end_session'}), name='pgp-key-end-session'),
    path('pgp-keys/session_status/', PGPKeyViewSet.as_view({'get': 'session_status'}), name='pgp-key-session-status'),
] 