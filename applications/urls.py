from django.urls import path

from .views import ApplicationListView

app_name = "applications"

urlpatterns = [
    path("", ApplicationListView.as_view(), name="application-list"),
]
