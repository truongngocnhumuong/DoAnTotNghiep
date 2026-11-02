"""
applications/views.py

Views đầy đủ cho SubTask 5.1–5.5:
  - ApplyView         : Nộp hồ sơ CV (GET form, POST lưu Application + lịch sử)
  - MyApplicationListView : Candidate xem danh sách hồ sơ của mình
  - ApplicationListView   : HR/Admin xem tất cả hồ sơ
  - ApplicationDetailView : Chi tiết hồ sơ (object-level check)
  - CVDownloadView    : Tải CV — yêu cầu đăng nhập + kiểm tra quyền
"""

import mimetypes
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from accounts.mixins import PERMISSION_DENIED_MESSAGE, CandidateRequiredMixin
from accounts.models import User
from applications.forms import ApplicationForm
from applications.models import Application, ApplicationStatusHistory
from jobs.models import JobPost


# ---------------------------------------------------------------------------
# Mixin dùng chung — lọc queryset theo role
# ---------------------------------------------------------------------------

class ApplicationQuerysetMixin(LoginRequiredMixin):
    """
    Candidate: chỉ thấy hồ sơ của mình.
    HR / Admin: thấy tất cả.
    """
    def get_queryset(self):
        qs = Application.objects.select_related("job_post", "candidate")
        role = getattr(self.request.user, "role", None)
        if role == User.Role.CANDIDATE:
            return qs.filter(candidate=self.request.user)
        if role in {User.Role.ADMIN, User.Role.HR}:
            return qs
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)


# ---------------------------------------------------------------------------
# SubTask 5.2 + 5.3 — Nộp hồ sơ
# ---------------------------------------------------------------------------

class ApplyView(CandidateRequiredMixin, View):
    """
    GET  : Hiển thị form upload CV.
    POST : Validate tệp → lưu Application (APPLIED, PENDING) + lịch sử.

    Các kiểm tra phía server:
      - Tin tuyển dụng phải OPEN + chưa hết hạn (is_open_for_applications)
      - Candidate chưa nộp hồ sơ cho tin này (UniqueConstraint)
      - Tệp CV hợp lệ (ApplicationForm: kích thước, extension, magic bytes)
    """

    def _get_job_or_404(self, job_pk):
        return get_object_or_404(JobPost, pk=job_pk)

    def get(self, request, job_pk):
        job = self._get_job_or_404(job_pk)

        # Kiểm tra tin còn nhận hồ sơ không
        if not job.is_open_for_applications:
            messages.error(request, "Tin tuyển dụng này đã đóng hoặc hết hạn.")
            return redirect("jobs:job-detail", pk=job_pk)

        # Kiểm tra đã nộp chưa
        if Application.objects.filter(job_post=job, candidate=request.user).exists():
            messages.info(request, "Bạn đã nộp hồ sơ cho vị trí này rồi.")
            return redirect("jobs:job-detail", pk=job_pk)

        form = ApplicationForm()
        return render(request, "applications/apply.html", {"form": form, "job": job})

    def post(self, request, job_pk):
        job = self._get_job_or_404(job_pk)

        # ── Kiểm tra server-side lần cuối ──
        if not job.is_open_for_applications:
            messages.error(request, "Tin tuyển dụng đã đóng. Không thể nộp hồ sơ.")
            return redirect("jobs:job-detail", pk=job_pk)

        if Application.objects.filter(job_post=job, candidate=request.user).exists():
            messages.warning(request, "Bạn đã nộp hồ sơ cho vị trí này rồi.")
            return redirect("applications:my-applications")

        form = ApplicationForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, "applications/apply.html", {"form": form, "job": job})

        cv_file = form.cleaned_data["cv_file"]
        original_name = cv_file.name  # tên gốc của tệp

        try:
            # ── SubTask 5.3: Lưu Application ──
            app = Application(
                job_post=job,
                candidate=request.user,
                cv_file=cv_file,
                cv_original_name=original_name,
                current_status=Application.Status.APPLIED,
                scoring_status=Application.ScoringStatus.PENDING,
                similarity_score=None,
                ranking_position=None,
            )
            app.save()  # lưu file lên disk, sinh UUID filename

            # ── SubTask 5.3: Lưu ApplicationStatusHistory (APPLIED, changed_by = Candidate) ──
            ApplicationStatusHistory.objects.create(
                application=app,
                from_status=None,       # bản ghi đầu tiên, không có trạng thái trước
                to_status=Application.Status.APPLIED,
                changed_by=request.user,  # chính Candidate
            )

            # ── Kích hoạt pipeline chấm điểm (Task 6 sẽ điền service) ──
            try:
                from applications.services import process_cv_and_score
                process_cv_and_score(app.pk)
            except Exception:
                # Service chưa có hoặc lỗi — bỏ qua, không crash view
                pass

            messages.success(
                request,
                f'Nộp hồ sơ thành công cho vị trí "{job.title}". '
                "Hệ thống đang xử lý CV của bạn.",
            )
            return redirect("applications:my-applications")

        except IntegrityError:
            # Race condition: 2 request cùng lúc — UniqueConstraint bắt
            messages.warning(request, "Bạn đã nộp hồ sơ cho vị trí này rồi.")
            return redirect("applications:my-applications")


# ---------------------------------------------------------------------------
# SubTask 5.4 — Candidate theo dõi hồ sơ
# ---------------------------------------------------------------------------

class MyApplicationListView(CandidateRequiredMixin, ListView):
    """
    Danh sách hồ sơ của Candidate đang đăng nhập.
    Lọc chặt theo request.user — không bao giờ lộ hồ sơ của người khác.
    """
    model = Application
    template_name = "applications/my_application_list.html"
    context_object_name = "applications"
    paginate_by = 15

    def get_queryset(self):
        return (
            Application.objects.filter(candidate=self.request.user)
            .select_related("job_post")
            .order_by("-applied_at")
        )


# ---------------------------------------------------------------------------
# HR / Admin — xem tất cả hồ sơ
# ---------------------------------------------------------------------------

class ApplicationListView(ApplicationQuerysetMixin, ListView):
    """Danh sách tất cả hồ sơ — HR/Admin."""
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().order_by("-applied_at")
        # Lọc theo job nếu có query param
        job_pk = self.request.GET.get("job", "").strip()
        if job_pk.isdigit():
            qs = qs.filter(job_post_id=int(job_pk))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_filter"] = self.request.GET.get("job", "")
        return context


class ApplicationDetailView(ApplicationQuerysetMixin, DetailView):
    """
    Chi tiết một hồ sơ.
    Object-level check được xử lý bởi ApplicationQuerysetMixin:
      - Candidate chỉ thấy hồ sơ của mình (404 nếu truy cập của người khác).
      - HR/Admin thấy tất cả.
    """
    model = Application
    template_name = "applications/application_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "job_post", "candidate"
        ).prefetch_related("status_history__changed_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = self.object
        context["status_history"] = app.status_history.select_related(
            "changed_by"
        ).order_by("changed_at")
        return context


# ---------------------------------------------------------------------------
# SubTask 5.5 — Tải CV (bảo vệ bằng auth + role check)
# ---------------------------------------------------------------------------

class CVDownloadView(LoginRequiredMixin, View):
    """
    Phục vụ file CV qua FileResponse.
    KHÔNG expose URL media trực tiếp.

    Quyền:
      - Candidate: chỉ tải CV của chính mình.
      - HR / Admin: tải bất kỳ CV nào.
    """

    def get(self, request, pk):
        app = get_object_or_404(
            Application.objects.select_related("candidate"),
            pk=pk,
        )
        user = request.user
        role = getattr(user, "role", None)

        # ── Kiểm tra quyền object-level ──
        if role == User.Role.CANDIDATE and app.candidate_id != user.pk:
            raise PermissionDenied("Bạn không có quyền tải CV của người khác.")

        if role not in {User.Role.CANDIDATE, User.Role.HR, User.Role.ADMIN}:
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        # ── Kiểm tra file tồn tại trên disk ──
        if not app.cv_file:
            raise Http404("Tệp CV không tồn tại.")

        file_path = app.cv_file.path
        if not os.path.isfile(file_path):
            raise Http404("Tệp CV không tìm thấy trên hệ thống.")

        # ── Xác định content-type ──
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"

        # ── Tên file gốc để gợi ý khi download ──
        download_name = app.cv_original_name or os.path.basename(file_path)

        response = FileResponse(
            open(file_path, "rb"),
            content_type=content_type,
            as_attachment=True,
            filename=download_name,
        )
        return response
