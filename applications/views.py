from django.views.generic import ListView

from .models import Application


class ApplicationListView(ListView):
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = Application.objects.select_related("job_post", "candidate")
        if self.request.user.is_authenticated and hasattr(self.request.user, "role"):
            if self.request.user.role == self.request.user.Role.CANDIDATE:
                return queryset.filter(candidate=self.request.user)
            if self.request.user.role in {self.request.user.Role.ADMIN, self.request.user.Role.HR}:
                return queryset
        return queryset.none()

# Create your views here.
