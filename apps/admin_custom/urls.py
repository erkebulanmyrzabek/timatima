from django.urls import path
from admin_custom.views import (
    AdminUserListCreateView,
    AdminUserRetrieveUpdateDestroyView
)

urlpatterns = [
    path('', AdminUserListCreateView.as_view(), name='admin-user-list-create'),
    path('<uuid:pk>/', AdminUserRetrieveUpdateDestroyView.as_view(), name='admin-user-detail'),
] 