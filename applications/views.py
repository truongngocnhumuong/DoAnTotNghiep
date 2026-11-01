from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from accounts.mixins import PERMISSION_DENIED_MESSAGE
from accounts.models import User
from applications.models import Application


class ApplicationQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        queryset = Application.objects.select_related("job_post", "candidate")
        role = getattr(self.request.user, "role", None)
        if role == User.Role.CANDIDATE:
            return queryset.filter(candidate=self.request.user)
        if role in {User.Role.ADMIN, User.Role.HR}:
            return queryset
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)


class ApplicationListView(ApplicationQuerysetMixin, ListView):
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"


class ApplicationDetailView(ApplicationQuerysetMixin, DetailView):
    model = Application
    template_name = "applications/application_detail.html"
    context_object_name = "application"


# ---------------------------------------------------------------------------
# Stub views — sẽ được thay thế đầy đủ ở Task 5
# ---------------------------------------------------------------------------

class MyApplicationListView(ApplicationQuerysetMixin, ListView):
    """Danh sách hồ sơ của Candidate đang đăng nhập."""
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"


class ApplyView(LoginRequiredMixin, View):
    """Nộp hồ sơ — stub placeholder (Task 5 sẽ hoàn thiện)."""

    def get(self, request, job_pk):
        # Stub: redirect về trang chi tiết job
        from jobs.models import JobPost
        job = get_object_or_404(JobPost, pk=job_pk)
        return redirect("jobs:job-detail", pk=job_pk)

    def post(self, request, job_pk):
        # Stub: sẽ xử lý upload CV ở Task 5
        return HttpResponse("Chuc nang dang duoc phat trien.", status=501)
