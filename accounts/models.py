from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.db import models


def normalize_user_email(email):
    if email is None:
        return email
    return str(email).strip().lower()


class UserManager(DjangoUserManager):
    @classmethod
    def normalize_email(cls, email):
        email = super().normalize_email(email)
        return normalize_user_email(email)

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("Tên đăng nhập là bắt buộc.")
        if email is None or not str(email).strip():
            raise ValueError("Email là bắt buộc.")
        if not extra_fields.get("full_name"):
            raise ValueError("Họ tên là bắt buộc.")
        extra_fields.setdefault("role", User.Role.CANDIDATE)
        return super()._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Quản trị"
        HR = "HR", "Nhân sự"
        CANDIDATE = "CANDIDATE", "Ứng viên"

    email = models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE,
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    objects = UserManager()

    REQUIRED_FIELDS = ["email", "full_name", "role"]

    class Meta:
        ordering = ["username"]
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        return f"{self.full_name or self.username} ({self.get_role_display()})"

    def clean(self):
        super().clean()
        if not self.email or not str(self.email).strip():
            raise ValidationError({"email": "Email là bắt buộc."})
        self.email = normalize_user_email(self.email)
        if not self.full_name or not str(self.full_name).strip():
            raise ValidationError({"full_name": "Họ tên là bắt buộc."})
        if not self.role:
            raise ValidationError({"role": "Vai trò là bắt buộc."})

    def save(self, *args, **kwargs):
        if self.email:
            self.email = normalize_user_email(self.email)
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hr_role(self):
        return self.role == self.Role.HR

    @property
    def is_candidate_role(self):
        return self.role == self.Role.CANDIDATE
