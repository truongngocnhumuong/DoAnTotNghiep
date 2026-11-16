# -*- coding: utf-8 -*-
"""
Management command: create_demo_data
Tao du lieu mau de demo he thong tuyen dung.
Chay: python manage.py create_demo_data
Chay lai an toan (dung get_or_create).
"""

import sys
from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def _make_minimal_pdf(title: str = "CV") -> bytes:
    """Tao file PDF toi thieu hop le theo chuan PDF 1.4."""
    # Use only ASCII in PDF content to avoid encoding issues
    safe_title = title.encode("ascii", errors="replace").decode("ascii")
    content_stream = f"BT /F1 12 Tf 72 720 Td ({safe_title}) Tj ET".encode("ascii")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 792] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        ),
        (
            f"4 0 obj\n<< /Length {len(content_stream)} >>\nstream\n".encode("ascii")
            + content_stream
            + b"\nendstream\nendobj\n"
        ),
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    header = b"%PDF-1.4\n"
    body = b""
    offsets = []
    pos = len(header)
    for obj in objects:
        offsets.append(pos)
        body += obj
        pos += len(obj)

    xref_offset = len(header) + len(body)
    xref = f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii")
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode("ascii")

    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode("ascii")

    return header + body + xref + trailer


def _p(msg: str) -> str:
    """Safe print: encode to ascii with replacement for Windows console."""
    return msg.encode("ascii", errors="replace").decode("ascii")


class Command(BaseCommand):
    help = "Tao du lieu mau de demo he thong tuyen dung nhan su."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Xoa toan bo du lieu demo truoc khi tao lai.",
        )

    def handle(self, *args, **options):
        from accounts.models import User
        from applications.models import Application, ApplicationStatusHistory, InterviewNote
        from applications.services import score_applications_for_job
        from jobs.models import JobPost

        if options["reset"]:
            self._reset_demo_data(User, Application, JobPost)

        self.stdout.write("=== Tao du lieu demo ===")

        # ── 1. Tai khoan ──────────────────────────────────────────────────────
        admin = self._get_or_create_user(
            User,
            username="admin_demo",
            email="admin@demo.com",
            full_name="Quan tri vien",
            role="ADMIN",
            password="Admin@1234",
        )
        hr = self._get_or_create_user(
            User,
            username="hr_demo",
            email="hr@demo.com",
            full_name="Nhan vien HR",
            role="HR",
            password="Hr@1234",
        )
        candidates = []
        for username, email, full_name in [
            ("candidate1_demo", "candidate1@demo.com", "Nguyen Van An"),
            ("candidate2_demo", "candidate2@demo.com", "Tran Thi Binh"),
            ("candidate3_demo", "candidate3@demo.com", "Le Minh Chau"),
        ]:
            c = self._get_or_create_user(
                User,
                username=username,
                email=email,
                full_name=full_name,
                role="CANDIDATE",
                password="Cand@1234",
            )
            candidates.append(c)

        # ── 2. Tin tuyen dung ─────────────────────────────────────────────────
        today = date.today()
        jobs_data = [
            {
                "title": "Lap trinh vien Python",
                "description": (
                    "Chung toi tim kiem lap trinh vien Python co kinh nghiem "
                    "xay dung ung dung web voi Django hoac FastAPI. "
                    "Lam viec trong moi truong Agile nang dong."
                ),
                "requirements": (
                    "- Thanh thao Python 3.x Django FastAPI\n"
                    "- Co kinh nghiem voi PostgreSQL SQLite\n"
                    "- Hieu biet ve REST API Git Docker\n"
                    "- Uu tien co kinh nghiem voi CI CD microservices"
                ),
                "benefits": "Luong 15-25 trieu VND thang. Thuong du an. Moi truong Agile.",
                "location": "Ha Noi",
                "department": "Cong nghe thong tin",
                "employment_type": "FULL_TIME",
                "status": JobPost.Status.OPEN,
                "deadline": today + timedelta(days=30),
            },
            {
                "title": "Nha thiet ke UI UX",
                "description": (
                    "Tim kiem nha thiet ke UI UX sang tao co tu duy nguoi dung "
                    "de thiet ke giao dien web va mobile app. "
                    "Phoi hop chat che voi team phat trien phan mem."
                ),
                "requirements": (
                    "- Thanh thao Figma Adobe XD hoac Sketch\n"
                    "- Co kinh nghiem thiet ke responsive web va mobile app\n"
                    "- Hieu biet ve HTML CSS co ban\n"
                    "- Portfolio da dang sang tao"
                ),
                "benefits": "Luong 12-20 trieu VND thang. Lam remote 2 ngay tuan.",
                "location": "Ho Chi Minh",
                "department": "Thiet ke",
                "employment_type": "FULL_TIME",
                "status": JobPost.Status.OPEN,
                "deadline": today + timedelta(days=15),
            },
            {
                "title": "Chuyen vien Marketing Digital",
                "description": (
                    "Tim chuyen vien Marketing Digital co kinh nghiem quan ly "
                    "chien dich quang cao truc tuyen SEO SEM va mang xa hoi."
                ),
                "requirements": (
                    "- Kinh nghiem 1-3 nam trong linh vuc Marketing Digital\n"
                    "- Thanh thao Google Ads Facebook Ads\n"
                    "- Co kinh nghiem SEO SEM Content Marketing\n"
                    "- Ky nang phan tich du lieu voi Google Analytics"
                ),
                "benefits": "Luong 10-18 trieu VND thang. Hoa hong theo KPI.",
                "location": "Da Nang",
                "department": "Marketing",
                "employment_type": "FULL_TIME",
                "status": JobPost.Status.CLOSED,
                "deadline": today + timedelta(days=5),
            },
        ]

        job_objects = []
        for jd in jobs_data:
            job, created = JobPost.objects.get_or_create(
                title=jd["title"],
                created_by=hr,
                defaults=jd,
            )
            if not created:
                for k, v in jd.items():
                    setattr(job, k, v)
                job.save(update_fields=list(jd.keys()))
            status_str = "[OK] Tao" if created else "[--] Cap nhat"
            self.stdout.write(f"  {status_str} tin: {job.title}")
            job_objects.append(job)

        # ── 3. Ho so ung tuyen ───────────────────────────────────────────────
        open_jobs = [j for j in job_objects if j.status == JobPost.Status.OPEN]
        app_objects = []

        for job in open_jobs:
            for candidate in candidates[:2]:
                app, created = Application.objects.get_or_create(
                    job_post=job,
                    candidate=candidate,
                    defaults={"current_status": Application.Status.APPLIED},
                )
                if created:
                    pdf_bytes = _make_minimal_pdf(f"CV {candidate.username}")
                    cv_filename = f"cv_{candidate.username}_{job.id}.pdf"
                    app.cv_file.save(cv_filename, ContentFile(pdf_bytes), save=True)

                    ApplicationStatusHistory.objects.get_or_create(
                        application=app,
                        to_status=Application.Status.APPLIED,
                        changed_by=candidate,
                        defaults={"from_status": None, "note": "Ung vien nop ho so."},
                    )
                    self.stdout.write(
                        f"    [OK] Ho so: {candidate.username} -> {job.title}"
                    )
                else:
                    self.stdout.write(
                        f"    [--] Ho so da ton tai: {candidate.username} -> {job.title}"
                    )
                app_objects.append(app)

        # ── 4. Chuyen trang thai mau ──────────────────────────────────────────
        if app_objects:
            first_app = app_objects[0]
            if first_app.current_status == Application.Status.APPLIED:
                first_app.current_status = Application.Status.REVIEWING
                first_app.save(update_fields=["current_status"])
                ApplicationStatusHistory.objects.get_or_create(
                    application=first_app,
                    to_status=Application.Status.REVIEWING,
                    changed_by=hr,
                    defaults={
                        "from_status": Application.Status.APPLIED,
                        "note": "HR chuyen sang dang xem xet.",
                    },
                )
                self.stdout.write(
                    f"    -> Chuyen trang thai {first_app.candidate.username}: APPLIED -> REVIEWING"
                )

        # ── 5. Ghi chu phong van mau ──────────────────────────────────────────
        if app_objects:
            InterviewNote.objects.get_or_create(
                application=app_objects[0],
                created_by=hr,
                defaults={
                    "title": "Ghi chu phong van vong 1",
                    "content": (
                        "Ung vien co nen tang Python tot, kinh nghiem voi Django "
                        "va REST API. Can kiem tra them ve ky nang DevOps. "
                        "De xuat moi phong van vong 2."
                    ),
                },
            )
            self.stdout.write("    [OK] Them ghi chu phong van mau")

        # ── 6. Cham diem CV ───────────────────────────────────────────────────
        self.stdout.write("Dang cham diem CV...")
        for job in open_jobs:
            try:
                score_applications_for_job(job.id)
                self.stdout.write(f"  [OK] Cham diem: {job.title}")
            except Exception as exc:
                self.stdout.write(f"  [!!] Loi cham diem {job.title}: {exc}")

        # ── Tong ket ──────────────────────────────────────────────────────────
        self.stdout.write("\n=== Tao du lieu demo thanh cong! ===")
        self.stdout.write("\nTai khoan demo:")
        self.stdout.write("  Admin : admin@demo.com    / Admin@1234")
        self.stdout.write("  HR    : hr@demo.com       / Hr@1234")
        self.stdout.write("  UV 1  : candidate1@demo.com / Cand@1234")
        self.stdout.write("  UV 2  : candidate2@demo.com / Cand@1234")
        self.stdout.write("  UV 3  : candidate3@demo.com / Cand@1234")
        self.stdout.write("\nChay server: python manage.py runserver")
        self.stdout.write("   Truy cap: http://127.0.0.1:8000/")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_or_create_user(self, User, username, email, full_name, role, password):
        user, created = User.objects.get_or_create(
            email=email.lower().strip(),
            defaults={
                "username": username,
                "full_name": full_name,
                "role": role,
                "is_active": True,
            },
        )
        if created:
            user.set_password(password)
            if role == "ADMIN":
                user.is_staff = True
                user.is_superuser = True
            user.save()
            self.stdout.write(f"  [OK] Tao user [{role}]: {email}")
        else:
            self.stdout.write(f"  [--] User da ton tai: {email}")
        return user

    def _reset_demo_data(self, User, Application, JobPost):
        self.stdout.write("[!!] Dang xoa du lieu demo cu...")
        demo_emails = [
            "admin@demo.com",
            "hr@demo.com",
            "candidate1@demo.com",
            "candidate2@demo.com",
            "candidate3@demo.com",
        ]
        demo_users = User.objects.filter(email__in=demo_emails)
        Application.objects.filter(candidate__in=demo_users).delete()
        JobPost.objects.filter(created_by__in=demo_users).delete()
        demo_users.delete()
        self.stdout.write("  [OK] Da xoa du lieu demo cu.")
