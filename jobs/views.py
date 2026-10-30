from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView

from .models import JobPost


class HomeView(TemplateView):
    template_name = "home.html"


class JobListView(LoginRequiredMixin, ListView):
    model = JobPost
    template_name = "jobs/job_list.html"
    context_object_name = "jobs"

    def get_queryset(self):
        return JobPost.objects.filter(status=JobPost.Status.OPEN).order_by(
            "deadline", "-created_at"
        )


class JobDetailView(LoginRequiredMixin, DetailView):
    model = JobPost
    template_name = "jobs/job_detail.html"
    context_object_name = "job"
