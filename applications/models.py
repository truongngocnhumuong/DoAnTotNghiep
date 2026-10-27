import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


def application_cv_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    return f"cvs/{uuid.uuid4().hex}{extension}"


def validate_cv_max_size(value):
    max_bytes = 5 * 1024 * 1024
    if value and getattr(value, "size", 0) > max_bytes:
        raise ValidationError("Dung lượng CV tối đa là 5 MB.")


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Đã nộp"
        REVIEWING = "REVIEWING", "Đang xét"
        INTERVIEW = "INTERVIEW", "Phỏng vấn"
        OFFERED = "OFFERED", "Đề nghị nhận việc"
        REJECTED = "REJECTED", "Từ chối"

    class ScoringStatus(models.TextChoices):
        PENDING = "PENDING", "Chờ chấm"
        SCORED = "SCORED", "Đã chấm"
        EXTRACTION_FAILED = "EXTRACTION_FAILED", "Lỗi trích xuất"
        INSUFFICIENT_TEXT = "INSUFFICIENT_TEXT", "Văn bản không đủ"
        SCORING_FAILED = "SCORING_FAILED", "Lỗi chấm điểm"

    job_post = models.ForeignKey(
        "jobs.JobPost",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="applications",
    )
    cv_file = models.FileField(
        upload_to=application_cv_upload_to,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "docx"]),
            validate_cv_max_size,
        ],
    )
    cv_original_name = models.CharField(max_length=255)
    cv_text = models.TextField(blank=True, null=True)
    scoring_status = models.CharField(
        max_length=30,
        choices=ScoringStatus.choices,
        default=ScoringStatus.PENDING,
    )
    similarity_score = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    ranking_position = models.IntegerField(blank=True, null=True)
    current_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.APPLIED,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        verbose_name = "Hồ sơ ứng tuyển"
        verbose_name_plural = "Hồ sơ ứng tuyển"
        constraints = [
            models.UniqueConstraint(
                fields=["job_post", "candidate"],
                name="unique_application_per_job_candidate",
            ),
            models.CheckConstraint(
                check=Q(similarity_score__isnull=True)
                | (Q(similarity_score__gte=0) & Q(similarity_score__lte=1)),
                name="application_similarity_score_range",
            ),
            models.CheckConstraint(
                check=Q(scoring_status="SCORED")
                | (Q(similarity_score__isnull=True) & Q(ranking_position__isnull=True)),
                name="application_score_only_when_scored",
            ),
        ]

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job_post.title}"

    def clean(self):
        super().clean()
        if self.candidate_id and self.candidate.role != self.candidate.Role.CANDIDATE:
            raise ValidationError({"candidate": "Chỉ tài khoản Ứng viên được nộp hồ sơ."})
        if not self.pk and self.job_post_id and not self.job_post.is_open_for_applications:
            raise ValidationError({"job_post": "Tin tuyển dụng này không còn nhận hồ sơ."})
        if self.scoring_status != self.ScoringStatus.SCORED:
            if self.similarity_score is not None or self.ranking_position is not None:
                raise ValidationError(
                    "Điểm phù hợp và thứ hạng chỉ được gán khi chấm thành công."
                )
        elif self.similarity_score is None:
            raise ValidationError(
                {"similarity_score": "Hồ sơ đã chấm phải có điểm phù hợp."}
            )

    def save(self, *args, **kwargs):
        if self.cv_file and not self.cv_original_name:
            self.cv_original_name = os.path.basename(self.cv_file.name)
        super().save(*args, **kwargs)


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    from_status = models.CharField(
        max_length=30,
        choices=Application.Status.choices,
        blank=True,
        null=True,
    )
    to_status = models.CharField(max_length=30, choices=Application.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="status_changes",
    )
    note = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Lịch sử trạng thái"
        verbose_name_plural = "Lịch sử trạng thái"

    def __str__(self):
        return f"{self.application} -> {self.to_status}"

    def is_initial_applied_record(self):
        return not self.from_status and self.to_status == Application.Status.APPLIED

    def clean(self):
        super().clean()
        if not self.changed_by_id:
            raise ValidationError({"changed_by": "Người thực hiện thay đổi là bắt buộc."})

        changed_by = self.changed_by
        if self.is_initial_applied_record():
            if changed_by.role != changed_by.Role.CANDIDATE:
                raise ValidationError(
                    {"changed_by": "Bản ghi nộp hồ sơ phải do chính ứng viên thực hiện."}
                )
            if self.application_id and changed_by.pk != self.application.candidate_id:
                raise ValidationError(
                    {"changed_by": "Người nộp phải là ứng viên của hồ sơ này."}
                )
            return

        if changed_by.role not in {changed_by.Role.ADMIN, changed_by.Role.HR}:
            raise ValidationError(
                {
                    "changed_by": "Chỉ Quản trị hoặc Nhân sự được đổi trạng thái sau khi nộp hồ sơ."
                }
            )


class InterviewNote(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interview_notes",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="interview_notes",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    interview_round = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ghi chú phỏng vấn"
        verbose_name_plural = "Ghi chú phỏng vấn"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.created_by_id and self.created_by.role not in {
            self.created_by.Role.ADMIN,
            self.created_by.Role.HR,
        }:
            raise ValidationError(
                {"created_by": "Chỉ Quản trị hoặc Nhân sự được tạo ghi chú phỏng vấn."}
            )
