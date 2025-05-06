from django.urls import path
from mainpage.views import (
    MainPageNewsView, MainPagePodcastsView, 
    MainPageTelegramPostsView, MainPageLawyersView
)

urlpatterns = [
    path('news/', MainPageNewsView.as_view(), name='mainpage-news'),
    path('podcasts/', MainPagePodcastsView.as_view(), name='mainpage-podcasts'),
    path('telegram-posts/', MainPageTelegramPostsView.as_view(), name='mainpage-telegram-posts'),
    path('lawyers/', MainPageLawyersView.as_view(), name='mainpage-lawyers'),
] 