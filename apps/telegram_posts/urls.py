from django.urls import path, include
from rest_framework.routers import DefaultRouter
from telegram_posts.views import TelegramPostViewSet

router = DefaultRouter()
router.register(r'', TelegramPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
