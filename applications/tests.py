from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, models
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from applications.models import Application, ApplicationStatusHistory, InterviewNote
from jobs.models import JobPost


class ApplicationModelTests(TestCase):
    def setUp(self):
        self.hr = User.objects.create_user(
            username="hr2",
            email="hr2@mail.com",
            password="MatKhauManh123",
            full_name="HR Two",
            role=User.Role.HR,
        )
        self.candidate = User.objects.create_user(
            username="uv2",
            email="uv2@mail.com",
            password="MatKhauManh123",
            full_name="Ung Vien Hai",
            role=User.Role.CANDIDATE,
        )
        self.other_candidate = User.objects.create_user(
            username="uv3",
            email="uv3@mail.com",
            password="MatKhauManh123",
            full_name="Ung Vien Ba",
            role=User.Role.CANDIDATE,
        )
        self.job = JobPost.objects.create(
            title="Nhan su",
            description="Mo ta JD",
            requirements="Yeu cau JD",
            deadline=timezone.localdate() + timedelta(days=10),
            status=JobPost.Status.OPEN,
            created_by=self.hr,
        )

    def _cv(self, name="cv.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 noi dung", content_type="application/pdf")

    def _application(self, candidate=None, **kwargs):
        defaults = {
            "job_post": self.job,
            "candidate": candidate or self.candidate,
            "cv_file": self._cv(),
            "cv_original_name": "cv.pdf",
        }
        defaults.update(kwargs)
        return Application.objects.create(**defaults)

    def test_unique_job_and_candidate(self):
        self._application()
        with self.assertRaises(IntegrityError):
            self._application()

    def test_candidate_on_delete_protect(self):
        self._application()
        with self.assertRaises(ProtectedError):
            self.candidate.delete()

    def test_status_choices_match_spec(self):
        self.assertEqual(
            [choice[0] for choice in Application.Status.choices],
            ["APPLIED", "REVIEWING", "INTERVIEW", "OFFERED", "REJECTED"],
        )

    def test_score_cannot_be_set_when_not_scored(self):
        application = Application(
            job_post=self.job,
            candidate=self.candidate,
            cv_file=self._cv(),
            cv_original_name="cv.pdf",
            scoring_status=Application.ScoringStatus.EXTRACTION_FAILED,
            similarity_score=0,
        )
        with self.assertRaises(ValidationError):
            application.full_clean()

    def test_database_rejects_score_when_not_scored(self):
        with self.assertRaises(IntegrityError):
            self._application(
                scoring_status=Application.ScoringStatus.INSUFFICIENT_TEXT,
                similarity_score=0,
            )

    def test_candidate_can_be_changed_by_on_applied_history(self):
        application = self._application()
        history = ApplicationStatusHistory(
            application=application,
            from_status=None,
            to_status=Application.Status.APPLIED,
            changed_by=self.candidate,
        )
        history.full_clean()
        history.save()
        self.assertEqual(application.status_history.count(), 1)

    def test_candidate_cannot_change_status_after_apply(self):
        application = self._application()
        history = ApplicationStatusHistory(
            application=application,
            from_status=Application.Status.APPLIED,
            to_status=Application.Status.REVIEWING,
            changed_by=self.candidate,
        )
        with self.assertRaises(ValidationError):
            history.full_clean()

    def test_changed_by_is_required_and_protected(self):
        application = self._application()
        history = ApplicationStatusHistory.objects.create(
            application=application,
            from_status=None,
            to_status=Application.Status.APPLIED,
            changed_by=self.candidate,
        )
        self.assertTrue(history.changed_by_id)
        with self.assertRaises(ProtectedError):
            self.candidate.delete()

    def test_interview_note_created_by_must_be_hr_or_admin(self):
        application = self._application()
        note = InterviewNote(
            application=application,
            created_by=self.candidate,
            title="Vong 1",
            content="Nhan xet",
        )
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_interview_note_created_by_hr(self):
        application = self._application()
        note = InterviewNote(
            application=application,
            created_by=self.hr,
            title="Vong 1",
            content="Nhan xet",
        )
        note.full_clean()
        note.save()
        self.assertEqual(application.interview_notes.count(), 1)
        self.assertIs(
            InterviewNote._meta.get_field("created_by").remote_field.on_delete,
            models.PROTECT,
        )
        self.assertIs(
            Application._meta.get_field("candidate").remote_field.on_delete,
            models.PROTECT,
        )
        self.assertIs(
            Application._meta.get_field("job_post").remote_field.on_delete,
            models.CASCADE,
        )
        self.assertIs(
            ApplicationStatusHistory._meta.get_field("changed_by").remote_field.on_delete,
            models.PROTECT,
        )


class ApplicationObjectPermissionTests(TestCase):
    def setUp(self):
        self.hr = User.objects.create_user(
            username="hrobj",
            email="hrobj@mail.com",
            password="MatKhauManh123",
            full_name="HR Obj",
            role=User.Role.HR,
        )
        self.candidate = User.objects.create_user(
            username="uvobj",
            email="uvobj@mail.com",
            password="MatKhauManh123",
            full_name="UV Obj",
            role=User.Role.CANDIDATE,
        )
        self.other = User.objects.create_user(
            username="uvkhac",
            email="uvkhac@mail.com",
            password="MatKhauManh123",
            full_name="UV Khac",
            role=User.Role.CANDIDATE,
        )
        job = JobPost.objects.create(
            title="Ky su",
            description="Mo ta",
            requirements="Yeu cau",
            deadline=timezone.localdate() + timedelta(days=5),
            status=JobPost.Status.OPEN,
            created_by=self.hr,
        )
        self.application = Application.objects.create(
            job_post=job,
            candidate=self.candidate,
            cv_file=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 x", content_type="application/pdf"),
            cv_original_name="cv.pdf",
        )

    def test_candidate_cannot_view_another_application(self):
        self.client.login(username="uvkhac", password="MatKhauManh123")
        url = reverse("applications:application-detail", args=[self.application.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_owner_and_hr_can_view_application(self):
        url = reverse("applications:application-detail", args=[self.application.pk])
        self.client.login(username="uvobj", password="MatKhauManh123")
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.logout()
        self.client.login(username="hrobj", password="MatKhauManh123")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_candidate_list_only_contains_own_applications(self):
        self.client.login(username="uvkhac", password="MatKhauManh123")
        response = self.client.get(reverse("applications:application-list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ky su")
        self.client.logout()
        self.client.login(username="uvobj", password="MatKhauManh123")
        own_list = self.client.get(reverse("applications:application-list"))
        self.assertContains(own_list, "Ky su")

    def test_anonymous_user_cannot_open_application(self):
        url = reverse("applications:application-detail", args=[self.application.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
