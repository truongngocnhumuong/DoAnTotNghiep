from django.core.exceptions import ValidationError
from django.urls import reverse

from accounts.models import User, normalize_user_email


def get_role_redirect_url(user):
    if user.role == User.Role.ADMIN:
        return reverse("accounts:user-list")
    if user.role == User.Role.HR:
        return reverse("dashboard:index")
    return reverse("jobs:job-list")


def validate_unique_normalized_email(email, instance=None):
    normalized = normalize_user_email(email)
    if not normalized:
        raise ValidationError("Email là bắt buộc.")
    queryset = User.objects.filter(email=normalized)
    if instance is not None and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    if queryset.exists():
        raise ValidationError("Email này đã được sử dụng.")
    return normalized
