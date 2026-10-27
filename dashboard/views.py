from django.views.generic import TemplateView

from applications.models import Application
from jobs.models import JobPost


class DashboardView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_jobs"] = JobPost.objects.count()
        context["open_jobs"] = JobPost.objects.filter(status=JobPost.Status.OPEN).count()
        context["total_applications"] = Application.objects.count()
        context["status_counts"] = {
            status: Application.objects.filter(current_status=status).count()
            for status, _ in Application.Status.choices
        }
        return context

# Create your views here.
