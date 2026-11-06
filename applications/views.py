"""
applications/views.py

Views đầy đủ Task 5 + Task 7:
  Task 5:
    ApplyView, MyApplicationListView, ApplicationListView,
    ApplicationDetailView, CVDownloadView

  Task 7:
    KanbanView          — Bảng Kanban kéo thả (SortableJS)
    UpdateStatusView    — POST JSON: chuyển trạng thái hợp lệ
    RestoreRejectedView — POST: khôi phục REJECTED (thao tác riêng)
    AddInterviewNoteView — POST: thêm ghi chú phỏng vấn
"""

import json
import mimetypes
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from accounts.mixins import (
    PERMISSION_DENIED_MESSAGE,
    CandidateRequiredMixin,
    StaffRequiredMixin,
)
from accounts.models import User
from applications.forms import ApplicationForm
from applications.models import Application, ApplicationStatusHistory, InterviewNote
from jobs.models import JobPost


# ────────────────────────────────────────────────────────────────────────────
# Hằng số Task 7
# ────────────────────────────────────────────────────────────────────────────

# Bảng chuyển trạng thái hợp lệ (thao tác thường — kéo thả Kanban)
VALID_TRANSITIONS = {
    Application.Status.APPLIED:    {Application.Status.REVIEWING, Application.Status.REJECTED},
    Application.Status.REVIEWING:  {Application.Status.APPLIED, Application.Status.INTERVIEW, Application.Status.REJECTED},
    Application.Status.INTERVIEW:  {Application.Status.REVIEWING, Application.Status.OFFERED, Application.Status.REJECTED},
    Application.Status.OFFERED:    {Application.Status.REJECTED},
    Application.Status.REJECTED:   set(),  # không cho kéo từ REJECTED sang bất kỳ đâu
}

# Trạng thái được phép khôi phục từ REJECTED (thao tác riêng)
RESTORE_TARGET = Application.Status.REVIEWING   # khôi phục về REVIEWING

# Thứ tự cột Kanban
KANBAN_COLUMNS = [
    (Application.Status.APPLIED,   "Đã nộp",             "secondary"),
    (Application.Status.REVIEWING, "Đang xét",           "info"),
    (Application.Status.INTERVIEW, "Phỏng vấn",          "primary"),
    (Application.Status.OFFERED,   "Đề nghị nhận việc",  "success"),
    (Application.Status.REJECTED,  "Từ chối",            "danger"),
]


# ────────────────────────────────────────────────────────────────────────────
# Mixin dùng chung — lọc queryset theo role
# ────────────────────────────────────────────────────────────────────────────

class ApplicationQuerysetMixin(LoginRequiredMixin):
    """Candidate: chỉ thấy hồ sơ của mình. HR/Admin: thấy tất cả."""

    def get_queryset(self):
        qs = Application.objects.select_related("job_post", "candidate")
        role = getattr(self.request.user, "role", None)
        if role == User.Role.CANDIDATE:
            return qs.filter(candidate=self.request.user)
        if role in {User.Role.ADMIN, User.Role.HR}:
            return qs
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)


# ────────────────────────────────────────────────────────────────────────────
# Task 5 — Nộp hồ sơ
# ────────────────────────────────────────────────────────────────────────────

class ApplyView(CandidateRequiredMixin, View):
    """GET: form upload CV. POST: validate + lưu Application + StatusHistory."""

    def _get_job(self, job_pk):
        return get_object_or_404(JobPost, pk=job_pk)

    def get(self, request, job_pk):
        job = self._get_job(job_pk)
        if not job.is_open_for_applications:
            messages.error(request, "Tin tuyển dụng này đã đóng hoặc hết hạn.")
            return redirect("jobs:job-detail", pk=job_pk)
        if Application.objects.filter(job_post=job, candidate=request.user).exists():
            messages.info(request, "Bạn đã nộp hồ sơ cho vị trí này rồi.")
            return redirect("jobs:job-detail", pk=job_pk)
        return render(request, "applications/apply.html", {"form": ApplicationForm(), "job": job})

    def post(self, request, job_pk):
        job = self._get_job(job_pk)
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
        try:
            app = Application(
                job_post=job, candidate=request.user,
                cv_file=cv_file, cv_original_name=cv_file.name,
                current_status=Application.Status.APPLIED,
                scoring_status=Application.ScoringStatus.PENDING,
                similarity_score=None, ranking_position=None,
            )
            app.save()
            ApplicationStatusHistory.objects.create(
                application=app, from_status=None,
                to_status=Application.Status.APPLIED, changed_by=request.user,
            )
            try:
                from applications.services import process_cv_and_score
                process_cv_and_score(app.pk)
            except Exception:
                pass
            messages.success(
                request,
                f'Nộp hồ sơ thành công cho vị trí "{job.title}". Hệ thống đang xử lý CV của bạn.',
            )
            return redirect("applications:my-applications")
        except IntegrityError:
            messages.warning(request, "Bạn đã nộp hồ sơ cho vị trí này rồi.")
            return redirect("applications:my-applications")


# ────────────────────────────────────────────────────────────────────────────
# Task 5 — Candidate theo dõi hồ sơ
# ────────────────────────────────────────────────────────────────────────────

class MyApplicationListView(CandidateRequiredMixin, ListView):
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


# ────────────────────────────────────────────────────────────────────────────
# Task 5 — HR/Admin xem tất cả hồ sơ
# ────────────────────────────────────────────────────────────────────────────

class ApplicationListView(ApplicationQuerysetMixin, ListView):
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().order_by("-applied_at")
        job_pk = self.request.GET.get("job", "").strip()
        if job_pk.isdigit():
            qs = qs.filter(job_post_id=int(job_pk))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_filter"] = self.request.GET.get("job", "")
        return context


class ApplicationDetailView(ApplicationQuerysetMixin, DetailView):
    """Chi tiết 1 hồ sơ (object-level check qua mixin)."""
    model = Application
    template_name = "applications/application_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "job_post", "candidate"
        ).prefetch_related("status_history__changed_by", "interview_notes__created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = self.object
        context["status_history"] = app.status_history.select_related(
            "changed_by"
        ).order_by("changed_at")
        context["interview_notes"] = app.interview_notes.select_related(
            "created_by"
        ).order_by("-created_at")
        context["is_hr_or_admin"] = getattr(self.request.user, "role", None) in {
            User.Role.HR, User.Role.ADMIN
        }
        context["VALID_TRANSITIONS"] = VALID_TRANSITIONS
        return context


# ────────────────────────────────────────────────────────────────────────────
# Task 5 — Tải CV
# ────────────────────────────────────────────────────────────────────────────

class CVDownloadView(LoginRequiredMixin, View):
    """Phục vụ file CV qua FileResponse — không expose URL media."""

    def get(self, request, pk):
        app = get_object_or_404(Application.objects.select_related("candidate"), pk=pk)
        user = request.user
        role = getattr(user, "role", None)
        if role == User.Role.CANDIDATE and app.candidate_id != user.pk:
            raise PermissionDenied("Bạn không có quyền tải CV của người khác.")
        if role not in {User.Role.CANDIDATE, User.Role.HR, User.Role.ADMIN}:
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
        if not app.cv_file:
            raise Http404("Tệp CV không tồn tại.")
        file_path = app.cv_file.path
        if not os.path.isfile(file_path):
            raise Http404("Tệp CV không tìm thấy trên hệ thống.")
        content_type, _ = mimetypes.guess_type(file_path)
        download_name = app.cv_original_name or os.path.basename(file_path)
        return FileResponse(
            open(file_path, "rb"),
            content_type=content_type or "application/octet-stream",
            as_attachment=True,
            filename=download_name,
        )


# ════════════════════════════════════════════════════════════════════════════
# Task 7 — Kanban
# ════════════════════════════════════════════════════════════════════════════

class KanbanView(StaffRequiredMixin, View):
    """
    SubTask 7.1 — Bảng Kanban kéo thả.
    Hiển thị tất cả hồ sơ của 1 JobPost theo cột trạng thái.
    """
    template_name = "applications/kanban.html"

    def get(self, request, job_pk):
        job = get_object_or_404(JobPost, pk=job_pk)
        all_apps = list(
            Application.objects.filter(job_post=job)
            .select_related("candidate")
            .order_by("ranking_position", "-applied_at")
        )
        # Tổ chức thành list các dict để template duyệt dễ dàng
        kanban_column_list = [
            {
                "status": status,
                "label":  label,
                "color":  color,
                "apps":   [a for a in all_apps if a.current_status == status],
            }
            for status, label, color in KANBAN_COLUMNS
        ]
        context = {
            "job": job,
            "kanban_column_list": kanban_column_list,
            "kanban_columns": KANBAN_COLUMNS,
            "total": len(all_apps),
        }
        return render(request, self.template_name, context)


class UpdateStatusView(StaffRequiredMixin, View):
    """
    SubTask 7.2 + 7.3 — Chuyển trạng thái hồ sơ qua POST JSON.

    Request body: {"application_id": <int>, "new_status": "<STATUS>"}
    Response JSON:
      - 200: {"ok": true, "new_status": "...", "new_status_display": "..."}
      - 400: {"ok": false, "error": "..."}
      - 403: {"ok": false, "error": "..."}
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"ok": False, "error": "Dữ liệu không hợp lệ."}, status=400)

        app_id = data.get("application_id")
        new_status = data.get("new_status", "").strip()

        if not app_id or not new_status:
            return JsonResponse(
                {"ok": False, "error": "Thiếu application_id hoặc new_status."}, status=400
            )

        app = get_object_or_404(Application, pk=app_id)
        old_status = app.current_status

        # ── No-op: cùng trạng thái ──────────────────────────────────────
        if old_status == new_status:
            return JsonResponse({"ok": True, "new_status": new_status,
                                  "new_status_display": app.get_current_status_display()})

        # ── Kiểm tra chuyển hợp lệ ──────────────────────────────────────
        allowed = VALID_TRANSITIONS.get(old_status, set())
        if new_status not in allowed:
            if old_status == Application.Status.REJECTED:
                error_msg = (
                    "Không thể kéo hồ sơ đã từ chối sang trạng thái khác. "
                    "Hãy dùng chức năng 'Khôi phục hồ sơ'."
                )
            else:
                error_msg = (
                    f"Không thể chuyển từ "
                    f'"{Application.Status(old_status).label}" '
                    f'sang "{Application.Status(new_status).label}".'
                )
            return JsonResponse({"ok": False, "error": error_msg}, status=400)

        # ── Cập nhật trạng thái ──────────────────────────────────────────
        Application.objects.filter(pk=app_id).update(current_status=new_status)

        # ── Ghi lịch sử (SubTask 7.3) ────────────────────────────────────
        ApplicationStatusHistory.objects.create(
            application=app,
            from_status=old_status,
            to_status=new_status,
            changed_by=request.user,
        )

        return JsonResponse({
            "ok": True,
            "new_status": new_status,
            "new_status_display": Application.Status(new_status).label,
        })


class RestoreRejectedView(StaffRequiredMixin, View):
    """
    SubTask 7.4 — Khôi phục hồ sơ REJECTED.
    GET : Trang xác nhận.
    POST: Thực hiện khôi phục về REVIEWING + ghi lịch sử.
    """

    def _get_app(self, pk):
        return get_object_or_404(Application.objects.select_related("job_post", "candidate"), pk=pk)

    def get(self, request, pk):
        app = self._get_app(pk)
        if app.current_status != Application.Status.REJECTED:
            messages.warning(request, "Hồ sơ này không ở trạng thái Từ chối.")
            return redirect("applications:application-detail", pk=pk)
        return render(request, "applications/restore_rejected_confirm.html", {"application": app})

    def post(self, request, pk):
        app = self._get_app(pk)
        if app.current_status != Application.Status.REJECTED:
            messages.warning(request, "Hồ sơ này không ở trạng thái Từ chối.")
            return redirect("applications:application-detail", pk=pk)

        old_status = app.current_status
        Application.objects.filter(pk=pk).update(current_status=RESTORE_TARGET)

        # Ghi lịch sử
        ApplicationStatusHistory.objects.create(
            application=app,
            from_status=old_status,
            to_status=RESTORE_TARGET,
            changed_by=request.user,
            note="Khôi phục hồ sơ từ Từ chối.",
        )

        messages.success(
            request,
            f'Đã khôi phục hồ sơ của "{app.candidate.full_name}" về trạng thái Đang xét.',
        )
        return redirect("applications:kanban", job_pk=app.job_post_id)


# ────────────────────────────────────────────────────────────────────────────
# Task 7.5 — Ghi chú phỏng vấn
# ────────────────────────────────────────────────────────────────────────────

class AddInterviewNoteView(StaffRequiredMixin, View):
    """
    SubTask 7.5 — Thêm ghi chú phỏng vấn cho 1 hồ sơ.
    POST (form submit) → redirect về application-detail.
    """

    def post(self, request, pk):
        app = get_object_or_404(Application, pk=pk)
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        interview_round = request.POST.get("interview_round", "").strip()

        if not title or not content:
            messages.error(request, "Tiêu đề và nội dung ghi chú không được để trống.")
            return redirect("applications:application-detail", pk=pk)

        InterviewNote.objects.create(
            application=app,
            created_by=request.user,
            title=title,
            content=content,
            interview_round=interview_round or None,
        )
        messages.success(request, "Đã thêm ghi chú phỏng vấn thành công.")
        return redirect("applications:application-detail", pk=pk)
