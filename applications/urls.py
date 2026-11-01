from django.urls import path

from .views import (
    ApplicationDetailView,
    ApplicationListView,
    ApplyView,
    MyApplicationListView,
)

app_name = "applications"

urlpatterns = [
    # Danh sách hồ sơ (HR/Admin xem tất cả; Candidate xem của mình)
    path("", ApplicationListView.as_view(), name="application-list"),
    # Hồ sơ của Candidate đang đăng nhập
    path("ho-so-cua-toi/", MyApplicationListView.as_view(), name="my-applications"),
    # Nộp hồ sơ cho 1 tin tuyển dụng — Task 5 sẽ hoàn thiện
    path("nop-ho-so/<int:job_pk>/", ApplyView.as_view(), name="apply"),
    # Chi tiết 1 hồ sơ
    path("<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
]
