from django.urls import path

from accounts.views import (
    CandidateRegistrationView,
    RoleBasedLoginView,
    RoleBasedLogoutView,
    UserCreateView,
    UserDetailView,
    UserListView,
    UserUpdateView,
)

app_name = "accounts"

urlpatterns = [
    path("dang-ky/", CandidateRegistrationView.as_view(), name="register"),
    path("dang-nhap/", RoleBasedLoginView.as_view(), name="login"),
    path("dang-xuat/", RoleBasedLogoutView.as_view(), name="logout"),
    path("nguoi-dung/", UserListView.as_view(), name="user-list"),
    path("nguoi-dung/tao/", UserCreateView.as_view(), name="user-create"),
    path("nguoi-dung/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("nguoi-dung/<int:pk>/sua/", UserUpdateView.as_view(), name="user-update"),
]
