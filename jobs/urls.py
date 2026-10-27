from django.urls import path

from .views import HomeView, JobDetailView, JobListView

app_name = "jobs"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("viec-lam/", JobListView.as_view(), name="job-list"),
    path("viec-lam/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
]
