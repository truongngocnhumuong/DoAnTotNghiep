from django.urls import path

from .views import (
    AddInterviewNoteView,
    ApplicationDetailView,
    ApplicationListView,
    ApplyView,
    CVDownloadView,
    KanbanView,
    MyApplicationListView,
    RestoreRejectedView,
    UpdateStatusView,
)

app_name = "applications"

urlpatterns = [
    # ── Candidate ──────────────────────────────────────────────────────────
    path("ho-so-cua-toi/", MyApplicationListView.as_view(), name="my-applications"),
    path("nop-ho-so/<int:job_pk>/", ApplyView.as_view(), name="apply"),
    path("<int:pk>/tai-cv/", CVDownloadView.as_view(), name="cv-download"),

    # ── HR / Admin — danh sách + chi tiết ──────────────────────────────────
    path("", ApplicationListView.as_view(), name="application-list"),
    path("<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),

    # ── Task 7: Kanban & chuyển trạng thái ─────────────────────────────────
    path("kanban/<int:job_pk>/", KanbanView.as_view(), name="kanban"),
    path("cap-nhat-trang-thai/", UpdateStatusView.as_view(), name="update-status"),
    path("<int:pk>/khoi-phuc/", RestoreRejectedView.as_view(), name="restore-rejected"),

    # ── Task 7.5: Ghi chú phỏng vấn ────────────────────────────────────────
    path("<int:pk>/ghi-chu/", AddInterviewNoteView.as_view(), name="add-note"),
]
