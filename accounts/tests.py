from django.contrib.auth.hashers import check_password, identify_hasher
from django.db import IntegrityError
from django.test import TestCase

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
