from django.urls import path, include
from rest_framework.routers import DefaultRouter
from podcasts.views import PodcastViewSet

router = DefaultRouter()
router.register(r'', PodcastViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
