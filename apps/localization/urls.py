from django.urls import path, include
from rest_framework.routers import DefaultRouter
from localization.views import LocalizationViewSet

router = DefaultRouter()
router.register(r'', LocalizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
