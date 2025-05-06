"""
URL configuration for dom_advokatov project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.accounts.urls import auth_urlpatterns, users_urlpatterns
# Описание API для документации Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Дом Адвокатов API",
        default_version='v1',
        description="API для юридического веб-сайта 'Дом Адвокатов'",
        contact=openapi.Contact(email="erkemyrzaa@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Функция для автоматического добавления url-путей API с префиксом версии
def get_versioned_api_urls(version='v1'):
    """
    Создает набор URL-путей для API с префиксом версии.
    
    Args:
        version (str): Версия API, по умолчанию 'v1'
        
    Returns:
        list: Список URL-путей с добавленным префиксом версии
    """
    return [
        # Авторизация и пользователи
        path(f'api/{version}/auth/', include(auth_urlpatterns)),
        path(f'api/{version}/users/', include(users_urlpatterns)),
        path(f'api/{version}/admin/users/', include('admin_custom.urls')),
        
        # Контент
        path(f'api/{version}/news/', include('news.urls')),
        path(f'api/{version}/podcasts/', include('podcasts.urls')),
        path(f'api/{version}/telegram-posts/', include('telegram_posts.urls')),
        path(f'api/{version}/lawyers/', include('lawyers.urls')),
        path(f'api/{version}/localization/', include('localization.urls')),
        path(f'api/{version}/mainpage/', include('mainpage.urls')),
        path(f'api/{version}/mail/', include('mail.urls')),
    ]

urlpatterns = [
    path('api/admin/', admin.site.urls),
    
    # Swagger/OpenAPI документация
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Добавляем URL-пути текущей версии API
urlpatterns.extend(get_versioned_api_urls())

# Для обратной совместимости оставляем старые URL-пути (без версии)
# В будущих обновлениях рекомендуется удалить эти пути
urlpatterns.extend([
    path('api/auth/', include(auth_urlpatterns)),
    path('api/users/', include(users_urlpatterns)),
    path('api/admin/users/', include('admin_custom.urls')),
    path('api/news/', include('news.urls')),
    path('api/podcasts/', include('podcasts.urls')),
    path('api/telegram-posts/', include('telegram_posts.urls')),
    path('api/lawyers/', include('lawyers.urls')),
    path('api/localization/', include('localization.urls')),
    path('api/mainpage/', include('mainpage.urls')),
    path('api/mail/', include('mail.urls')),
])

# Добавляем маршруты для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])