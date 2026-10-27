from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from jobs.models import JobPost


class JobPostModelTests(TestCase):
    def setUp(self):
        self.hr = User.objects.create_user(
            username="hr1",
            email="hr1@mail.com",
            password="MatKhauManh123",
            full_name="Tran Thi HR",
            role=User.Role.HR,
        )
        self.candidate = User.objects.create_user(
            username="uv1",
            email="uv1@mail.com",
            password="MatKhauManh123",
            full_name="Ung Vien",
            role=User.Role.CANDIDATE,
        )

    def test_created_by_must_be_hr_or_admin(self):
        job = JobPost(
            title="Lap trinh vien Python",
            description="Mo ta",
            requirements="Yeu cau",
            deadline=timezone.localdate() + timedelta(days=7),
            status=JobPost.Status.OPEN,
            created_by=self.candidate,
        )
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_created_by_is_protected(self):
        JobPost.objects.create(
            title="Lap trinh vien Python",
            description="Mo ta",
            requirements="Yeu cau",
            deadline=timezone.localdate() + timedelta(days=7),
            status=JobPost.Status.OPEN,
            created_by=self.hr,
        )
        with self.assertRaises(ProtectedError):
            self.hr.delete()
