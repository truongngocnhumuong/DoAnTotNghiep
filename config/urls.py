"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Quản trị hệ thống tuyển dụng"
admin.site.site_title = "Tuyển dụng"
admin.site.index_title = "Bảng điều khiển phát triển"

handler403 = "django.views.defaults.permission_denied"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("applications/", include("applications.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("jobs.urls")),
]
