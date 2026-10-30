from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.urls import reverse_lazy, reverse

from accounts.mixins import StaffRequiredMixin
from .forms import JobPostForm
from .models import JobPost


# ---------------------------------------------------------------------------
# Views dùng chung
# ---------------------------------------------------------------------------

class HomeView(TemplateView):
    template_name = "home.html"


# ---------------------------------------------------------------------------
# Views dành cho Candidate — chỉ thấy tin OPEN, chưa hết hạn
# ---------------------------------------------------------------------------

class JobListView(LoginRequiredMixin, ListView):
    """Danh sách tin tuyển dụng đang mở — dành cho Candidate xem."""
    model = JobPost
    template_name = "jobs/job_list.html"
    context_object_name = "jobs"

    def get_queryset(self):
        from django.utils import timezone
        return (
            JobPost.objects.filter(status=JobPost.Status.OPEN)
            .filter(deadline__gte=timezone.localdate())
            .order_by("deadline", "-created_at")
        )


class JobDetailView(LoginRequiredMixin, DetailView):
    """Chi tiết tin tuyển dụng — Candidate xem, có nút nộp hồ sơ."""
    model = JobPost
    template_name = "jobs/job_detail.html"
    context_object_name = "job"

    def get_queryset(self):
        """Candidate chỉ xem tin OPEN; HR/Admin xem tất cả."""
        user = self.request.user
        if hasattr(user, "role") and user.role in ("HR", "ADMIN"):
            return JobPost.objects.all()
        from django.utils import timezone
        return (
            JobPost.objects.filter(status=JobPost.Status.OPEN)
            .filter(deadline__gte=timezone.localdate())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        job = self.object
        # Kiểm tra ứng viên đã nộp chưa
        already_applied = False
        if hasattr(user, "role") and user.role == "CANDIDATE":
            from applications.models import Application
            already_applied = Application.objects.filter(
                job_post=job, candidate=user
            ).exists()
        context["already_applied"] = already_applied
        context["is_open"] = job.is_open_for_applications
        return context


# ---------------------------------------------------------------------------
# Views HR / Admin — quản lý tin tuyển dụng (SubTask 4.1)
# ---------------------------------------------------------------------------

class HRJobListView(StaffRequiredMixin, ListView):
    """Danh sách tất cả tin tuyển dụng — HR/Admin quản lý."""
    model = JobPost
    template_name = "jobs/hr_job_list.html"
    context_object_name = "jobs"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            JobPost.objects.select_related("created_by")
            .annotate(application_count=Count("applications"))
            .order_by("-created_at")
        )
        # Lọc theo trạng thái
        status_filter = self.request.GET.get("status", "").strip()
        if status_filter in JobPost.Status.values:
            qs = qs.filter(status=status_filter)
        # Tìm kiếm theo tiêu đề
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(department__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = JobPost.Status.choices
        context["status_filter"] = self.request.GET.get("status", "")
        context["q"] = self.request.GET.get("q", "")
        return context


class HRJobCreateView(StaffRequiredMixin, CreateView):
    """Tạo tin tuyển dụng mới — HR/Admin."""
    model = JobPost
    form_class = JobPostForm
    template_name = "jobs/hr_job_form.html"

    def get_success_url(self):
        return reverse("jobs:hr-job-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Gán created_by = user đang đăng nhập
        form.instance.created_by = self.request.user
        messages.success(self.request, "Đã tạo tin tuyển dụng thành công.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Tạo tin tuyển dụng mới"
        context["submit_label"] = "Tạo tin"
        return context


class HRJobUpdateView(StaffRequiredMixin, UpdateView):
    """Chỉnh sửa tin tuyển dụng — HR/Admin."""
    model = JobPost
    form_class = JobPostForm
    template_name = "jobs/hr_job_form.html"

    def get_success_url(self):
        return reverse("jobs:hr-job-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Ghi nhớ các trường JD trước khi lưu để kiểm tra thay đổi
        old = JobPost.objects.get(pk=self.object.pk)
        jd_changed = (
            old.title != form.cleaned_data.get("title")
            or old.description != form.cleaned_data.get("description")
            or old.requirements != form.cleaned_data.get("requirements")
        )
        response = super().form_valid(form)
        # SubTask 4.4 hook: tính lại điểm nếu JD thay đổi (sẽ nối sau Task 6)
        if jd_changed:
            self._trigger_rescore()
        messages.success(self.request, "Đã cập nhật tin tuyển dụng thành công.")
        return response

    def _trigger_rescore(self):
        """Hook gọi lại pipeline chấm điểm khi JD thay đổi (Task 6 sẽ điền)."""
        try:
            from applications.services import score_applications_for_job
            score_applications_for_job(self.object.pk)
        except Exception:
            # Service chưa tồn tại hoặc lỗi — bỏ qua, không crash view
            pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Chỉnh sửa: {self.object.title}"
        context["submit_label"] = "Lưu thay đổi"
        return context


class HRJobDetailView(StaffRequiredMixin, DetailView):
    """Chi tiết tin tuyển dụng — HR/Admin xem JD và danh sách ứng viên."""
    model = JobPost
    template_name = "jobs/hr_job_detail.html"
    context_object_name = "job"

    def get_queryset(self):
        return JobPost.objects.select_related("created_by").prefetch_related("applications")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        # Danh sách hồ sơ của tin này, sắp xếp ranking_position tăng dần
        applications = (
            job.applications
            .select_related("candidate")
            .order_by(
                # SCORED (có ranking_position) lên trước, NULL xuống dưới
                "ranking_position",    # NULL luôn xuống cuối trong SQLite
                "-applied_at",
            )
        )
        # Tổng hợp trạng thái
        status_counts = {}
        for app in applications:
            status_counts[app.current_status] = status_counts.get(app.current_status, 0) + 1

        context["applications"] = applications
        context["application_count"] = applications.count()
        context["status_counts"] = status_counts
        return context
