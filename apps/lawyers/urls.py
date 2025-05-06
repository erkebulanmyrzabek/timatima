from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lawyers.views import LawyerViewSet

router = DefaultRouter()
router.register(r'', LawyerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
