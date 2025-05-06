from django.urls import path, include
from rest_framework.routers import DefaultRouter
from mail.views import MailViewSet, MailAttachmentViewSet

router = DefaultRouter()
router.register(r'', MailViewSet, basename='mail')

# Создаем отдельный роутер для вложений
attachments_router = DefaultRouter()
attachments_router.register(r'', MailAttachmentViewSet, basename='mail-attachments')

urlpatterns = [
    path('', include(router.urls)),
    path('inbox/', MailViewSet.as_view({'get': 'inbox'}), name='mail-inbox'),
    path('sent/', MailViewSet.as_view({'get': 'sent'}), name='mail-sent'),
    path('drafts/', MailViewSet.as_view({'get': 'drafts'}), name='mail-drafts'),
    path('trash/', MailViewSet.as_view({'get': 'trash'}), name='mail-trash'),
    path('attachments/', include(attachments_router.urls)),
] 