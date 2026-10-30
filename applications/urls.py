from django.urls import path

from .views import ApplicationDetailView, ApplicationListView

app_name = "applications"

urlpatterns = [
    path("", ApplicationListView.as_view(), name="application-list"),
    path("<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
]
