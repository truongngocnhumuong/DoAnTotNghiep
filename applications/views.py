from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
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
