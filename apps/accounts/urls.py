from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import (
    LoginView, RegisterView,
    UpdateProfileView, Update2FAView, DeleteAccountView,
    UserByEmailView
)

# Маршруты авторизации
auth_urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Маршруты пользователей
users_urlpatterns = [
    path('profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('update-2fa/', Update2FAView.as_view(), name='update_2fa'),
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),
    path('by-email/', UserByEmailView.as_view(), name='user_by_email'),
]

urlpatterns = []  # Этот список будет использоваться в core/urls.py 