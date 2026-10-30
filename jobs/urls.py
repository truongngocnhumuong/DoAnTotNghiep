from django.urls import path

from .views import (
    HomeView,
    HRJobCreateView,
    HRJobDetailView,
    HRJobListView,
    HRJobUpdateView,
    JobDetailView,
    JobListView,
)

app_name = "jobs"

urlpatterns = [
    # Trang chủ
    path("", HomeView.as_view(), name="home"),

    # Candidate: xem tin tuyển dụng đang mở
    path("viec-lam/", JobListView.as_view(), name="job-list"),
    path("viec-lam/<int:pk>/", JobDetailView.as_view(), name="job-detail"),

    # HR / Admin: quản lý tin tuyển dụng
    path("quan-ly/tin-tuyen-dung/", HRJobListView.as_view(), name="hr-job-list"),
    path("quan-ly/tin-tuyen-dung/tao/", HRJobCreateView.as_view(), name="hr-job-create"),
    path("quan-ly/tin-tuyen-dung/<int:pk>/", HRJobDetailView.as_view(), name="hr-job-detail"),
    path("quan-ly/tin-tuyen-dung/<int:pk>/sua/", HRJobUpdateView.as_view(), name="hr-job-update"),
]
