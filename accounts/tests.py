from django.contrib.auth.hashers import check_password, identify_hasher
from django.contrib.messages import get_messages
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from accounts.forms import DjangoAdminUserCreationForm
from accounts.models import User, normalize_user_email


class UserModelTests(TestCase):
    def test_create_user_hashes_password_with_django(self):
        user = User.objects.create_user(
            username="ungvien1",
            email="UngVien@Mail.com",
            password="MatKhauManh123",
            full_name="Nguyen Van A",
        )
        self.assertNotEqual(user.password, "MatKhauManh123")
        identify_hasher(user.password)
        self.assertTrue(check_password("MatKhauManh123", user.password))
        self.assertEqual(user.role, User.Role.CANDIDATE)

    def test_email_is_normalized_before_save(self):
        self.assertEqual(normalize_user_email("  A@Mail.COM "), "a@mail.com")
        user = User.objects.create_user(
            username="ungvien2",
            email="  A@Mail.COM ",
            password="MatKhauManh123",
            full_name="Nguyen Van B",
        )
        self.assertEqual(user.email, "a@mail.com")

    def test_duplicate_email_after_normalization_is_rejected(self):
        User.objects.create_user(
            username="ungvien3",
            email="a@mail.com",
            password="MatKhauManh123",
            full_name="Nguyen Van C",
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="ungvien4",
                email="A@Mail.com",
                password="MatKhauManh123",
                full_name="Nguyen Van D",
            )

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username="ungvien5",
                email="",
                password="MatKhauManh123",
                full_name="Nguyen Van E",
            )


class AuthenticationFlowTests(TestCase):
    def test_register_creates_candidate_then_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "ungvienmoi",
                "email": "  New.User@Mail.COM ",
                "full_name": "Ung Vien Moi",
                "password": "MatKhauManh123",
                "confirm_password": "MatKhauManh123",
                "role": User.Role.ADMIN,
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(
            any("Đăng ký thành công" in str(message) for message in get_messages(response.wsgi_request))
        )
        user = User.objects.get(username="ungvienmoi")
        self.assertEqual(user.role, User.Role.CANDIDATE)
        self.assertEqual(user.email, "new.user@mail.com")
        self.assertTrue(user.is_active)
        self.assertTrue(check_password("MatKhauManh123", user.password))

    def test_register_creates_hr_then_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "hrmoi",
                "email": "  HR.New@Mail.COM ",
                "full_name": "HR Moi",
                "password": "MatKhauManh123",
                "confirm_password": "MatKhauManh123",
                "role": User.Role.HR,
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        user = User.objects.get(username="hrmoi")
        self.assertEqual(user.role, User.Role.HR)
        self.assertEqual(user.email, "hr.new@mail.com")
        self.assertTrue(user.is_active)
        self.assertTrue(check_password("MatKhauManh123", user.password))

    def test_login_redirects_by_role(self):
        User.objects.create_user(
            username="admin1",
            email="admin1@mail.com",
            password="MatKhauManh123",
            full_name="Admin Mot",
            role=User.Role.ADMIN,
        )
        User.objects.create_user(
            username="hrlogin",
            email="hrlogin@mail.com",
            password="MatKhauManh123",
            full_name="HR Login",
            role=User.Role.HR,
        )
        User.objects.create_user(
            username="uvlogin",
            email="uvlogin@mail.com",
            password="MatKhauManh123",
            full_name="UV Login",
            role=User.Role.CANDIDATE,
        )

        admin_response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin1", "password": "MatKhauManh123"},
        )
        self.assertRedirects(admin_response, reverse("accounts:user-list"))
        self.client.logout()

        hr_response = self.client.post(
            reverse("accounts:login"),
            {"username": "hrlogin", "password": "MatKhauManh123"},
        )
        self.assertRedirects(hr_response, reverse("dashboard:index"))
        self.client.logout()

        candidate_response = self.client.post(
            reverse("accounts:login"),
            {"username": "uvlogin", "password": "MatKhauManh123"},
        )
        self.assertRedirects(candidate_response, reverse("jobs:job-list"))

    def test_inactive_user_cannot_login(self):
        User.objects.create_user(
            username="khoa1",
            email="khoa1@mail.com",
            password="MatKhauManh123",
            full_name="Tai Khoan Khoa",
            role=User.Role.CANDIDATE,
            is_active=False,
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "khoa1", "password": "MatKhauManh123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_role_mixins_block_wrong_role(self):
        User.objects.create_user(
            username="uvblock",
            email="uvblock@mail.com",
            password="MatKhauManh123",
            full_name="UV Block",
            role=User.Role.CANDIDATE,
        )
        User.objects.create_user(
            username="hrblock",
            email="hrblock@mail.com",
            password="MatKhauManh123",
            full_name="HR Block",
            role=User.Role.HR,
        )
        self.client.login(username="uvblock", password="MatKhauManh123")
        self.assertEqual(self.client.get(reverse("accounts:user-list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:index")).status_code, 403)
        self.client.logout()
        self.client.login(username="hrblock", password="MatKhauManh123")
        self.assertEqual(self.client.get(reverse("accounts:user-list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:index")).status_code, 200)

    def test_admin_can_view_user_detail(self):
        admin = User.objects.create_user(
            username="admin2",
            email="admin2@mail.com",
            password="MatKhauManh123",
            full_name="Admin Hai",
            role=User.Role.ADMIN,
        )
        target = User.objects.create_user(
            username="candidate_view",
            email="view@mail.com",
            password="MatKhauManh123",
            full_name="Candidate View",
            role=User.Role.CANDIDATE,
        )
        self.client.login(username="admin2", password="MatKhauManh123")
        response = self.client.get(reverse("accounts:user-detail", args=[target.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Candidate View")

    def test_django_admin_creation_form_requires_role_and_unique_email(self):
        User.objects.create_user(
            username="coemail",
            email="trung@mail.com",
            password="MatKhauManh123",
            full_name="Co Email",
            role=User.Role.CANDIDATE,
        )
        form = DjangoAdminUserCreationForm(
            data={
                "username": "adminform",
                "email": "  Trung@Mail.com ",
                "full_name": "Admin Form",
                "role": User.Role.ADMIN,
                "password1": "MatKhauManh123",
                "password2": "MatKhauManh123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_logout_requires_post_and_clears_session(self):
        User.objects.create_user(
            username="uvout",
            email="uvout@mail.com",
            password="MatKhauManh123",
            full_name="UV Out",
            role=User.Role.CANDIDATE,
        )
        self.client.login(username="uvout", password="MatKhauManh123")
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("jobs:home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_can_lock_and_unlock_account(self):
        admin = User.objects.create_user(
            username="adminlock",
            email="adminlock@mail.com",
            password="MatKhauManh123",
            full_name="Admin Lock",
            role=User.Role.ADMIN,
        )
        target = User.objects.create_user(
            username="hrkhoa",
            email="hrkhoa@mail.com",
            password="MatKhauManh123",
            full_name="HR Khoa",
            role=User.Role.HR,
        )
        self.client.login(username="adminlock", password="MatKhauManh123")
        
        # Test khóa tài khoản
        response = self.client.post(reverse("accounts:user-toggle-active", args=[target.pk]))
        self.assertRedirects(response, reverse("accounts:user-list"))
        target.refresh_from_db()
        self.assertFalse(target.is_active)

        # Test mở khóa lại tài khoản
        response2 = self.client.post(reverse("accounts:user-toggle-active", args=[target.pk]))
        self.assertRedirects(response2, reverse("accounts:user-list"))
        target.refresh_from_db()
        self.assertTrue(target.is_active)

        # Test Admin không thể tự khóa chính mình
        self.client.post(reverse("accounts:user-toggle-active", args=[admin.pk]))
        admin.refresh_from_db()
        self.assertTrue(admin.is_active)
