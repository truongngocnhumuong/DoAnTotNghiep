from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class JobPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Nháp"
        OPEN = "OPEN", "Đang mở"
        CLOSED = "CLOSED", "Đã đóng"

    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    employment_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True, null=True)
    deadline = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="job_posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tin tuyển dụng"
        verbose_name_plural = "Tin tuyển dụng"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.created_by_id:
            created_by = self.created_by
            if created_by.role not in {created_by.Role.ADMIN, created_by.Role.HR}:
                raise ValidationError(
                    {"created_by": "Chỉ Quản trị hoặc Nhân sự được tạo tin tuyển dụng."}
                )
        if (
            self.status == self.Status.OPEN
            and self.deadline
            and self.deadline < timezone.localdate()
        ):
            raise ValidationError(
                {"deadline": "Hạn nộp không được nhỏ hơn ngày hiện tại khi tin đang mở tuyển."}
            )

    @property
    def is_open_for_applications(self):
        return self.status == self.Status.OPEN and self.deadline >= timezone.localdate()

    def jd_text_source(self):
        return " ".join(
            part.strip()
            for part in (self.title, self.description, self.requirements)
            if part
        )
