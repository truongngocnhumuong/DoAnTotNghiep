from django.urls import path

from .views import (
    ApplicationDetailView,
    ApplicationListView,
    ApplyView,
    CVDownloadView,
    MyApplicationListView,
)

app_name = "applications"

urlpatterns = [
    # ── Candidate ──
    # Danh sách hồ sơ của Candidate đang đăng nhập
    path("ho-so-cua-toi/", MyApplicationListView.as_view(), name="my-applications"),
    # Nộp hồ sơ cho 1 tin tuyển dụng
    path("nop-ho-so/<int:job_pk>/", ApplyView.as_view(), name="apply"),
    # Tải CV (auth + object-level check)
    path("<int:pk>/tai-cv/", CVDownloadView.as_view(), name="cv-download"),

    # ── HR / Admin ──
    # Danh sách tất cả hồ sơ
    path("", ApplicationListView.as_view(), name="application-list"),
    # Chi tiết 1 hồ sơ
    path("<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
]
