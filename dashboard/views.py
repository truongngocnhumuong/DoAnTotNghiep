"""
dashboard/views.py

Task 8 — Dashboard tuyển dụng:
  8.1: Truy vấn tổng hợp số liệu
  8.2: Thẻ thống kê tổng quan
  8.3: Biểu đồ Chart.js (pie trạng thái, bar top 5 jobs)
"""

import json

from django.db.models import Avg, Count
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from accounts.mixins import StaffRequiredMixin
from applications.models import Application
from jobs.models import JobPost


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ── 8.1a Thống kê tổng quan ──────────────────────────────────────
        total_jobs         = JobPost.objects.count()
        open_jobs          = JobPost.objects.filter(status=JobPost.Status.OPEN).count()
        total_applications = Application.objects.count()

        # Số lượng hồ sơ theo từng trạng thái
        status_counts = {
            status: Application.objects.filter(current_status=status).count()
            for status, _ in Application.Status.choices
        }

        # ── 8.1b Tỷ lệ OFFERED = (số OFFERED / tổng hồ sơ) × 100% ──────
        offered_count = status_counts.get(Application.Status.OFFERED, 0)
        if total_applications > 0:
            offered_rate = round(offered_count / total_applications * 100, 1)
        else:
            offered_rate = 0.0

        # ── 8.1c Điểm phù hợp trung bình — chỉ hồ sơ SCORED ────────────
        avg_score_result = Application.objects.filter(
            scoring_status=Application.ScoringStatus.SCORED,
            similarity_score__isnull=False,
        ).aggregate(avg=Avg("similarity_score"))
        avg_score = avg_score_result["avg"]
        if avg_score is not None:
            avg_score = round(avg_score, 3)

        # ── 8.1d Top 5 tin tuyển dụng có nhiều hồ sơ nhất ───────────────
        top_jobs = list(
            JobPost.objects.annotate(app_count=Count("applications"))
            .filter(app_count__gt=0)
            .order_by("-app_count")[:5]
        )

        # ── Màu sắc theo trạng thái ──────────────────────────────────────
        status_colors = {
            Application.Status.APPLIED:   "#6c757d",
            Application.Status.REVIEWING: "#0dcaf0",
            Application.Status.INTERVIEW: "#0d6efd",
            Application.Status.OFFERED:   "#198754",
            Application.Status.REJECTED:  "#dc3545",
        }
        status_css = {
            Application.Status.APPLIED:   "secondary",
            Application.Status.REVIEWING: "info",
            Application.Status.INTERVIEW: "primary",
            Application.Status.OFFERED:   "success",
            Application.Status.REJECTED:  "danger",
        }

        # ── Danh sách rows cho template ──────────────────────────────────
        status_rows = [
            {
                "status": status,
                "label":  label,
                "count":  status_counts.get(status, 0),
                "css":    status_css.get(status, "light"),
            }
            for status, label in Application.Status.choices
        ]

        # ── Dữ liệu JSON cho Chart.js ────────────────────────────────────
        status_labels_list = [label for _, label in Application.Status.choices]
        status_data_list   = [status_counts.get(s, 0) for s, _ in Application.Status.choices]
        status_color_list  = [status_colors.get(s, "#aaa") for s, _ in Application.Status.choices]

        top_job_labels = [
            j.title[:30] + ("…" if len(j.title) > 30 else "")
            for j in top_jobs
        ]
        top_job_data = [j.app_count for j in top_jobs]

        context.update({
            # Thẻ thống kê
            "total_jobs":         total_jobs,
            "open_jobs":          open_jobs,
            "total_applications": total_applications,
            "offered_count":      offered_count,
            "offered_rate":       offered_rate,
            "avg_score":          avg_score,
            "status_rows":        status_rows,
            "top_jobs":           top_jobs,

            # Chart.js — mark_safe vì đây là JSON do server tạo, không phải user input
            "chart_status_labels":  mark_safe(json.dumps(status_labels_list, ensure_ascii=False)),
            "chart_status_data":    mark_safe(json.dumps(status_data_list)),
            "chart_status_colors":  mark_safe(json.dumps(status_color_list)),
            "chart_top_job_labels": mark_safe(json.dumps(top_job_labels, ensure_ascii=False)),
            "chart_top_job_data":   mark_safe(json.dumps(top_job_data)),
        })
        return context

