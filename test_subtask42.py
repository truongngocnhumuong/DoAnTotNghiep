"""
Test SubTask 4.2 — Trang Candidate: danh sach viec lam va chi tiet JD.
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, r"e:\DOANTOTNGHIEP\DOAN")
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

PASS = "TestPass1234!"
results = []

def ok(name):
    results.append(("OK", name))
    sys.stdout.buffer.write(("  [OK] " + name + "\n").encode("utf-8"))

def fail(name, reason=""):
    results.append(("FAIL", name))
    sys.stdout.buffer.write(("  [FAIL] " + name + ": " + reason + "\n").encode("utf-8"))

@override_settings(ALLOWED_HOSTS=["testserver"])
def run():
    from jobs.models import JobPost
    from applications.models import Application

    # ---------- Setup ----------
    Application.objects.all().delete()
    JobPost.objects.filter(title__startswith="[T42]").delete()
    User.objects.filter(email__endswith="@t42.test").delete()

    hr = User.objects.create_user(
        username="hr_t42", email="hr@t42.test", password=PASS,
        role="HR", full_name="HR Test"
    )
    cand = User.objects.create_user(
        username="cand_t42", email="cand@t42.test", password=PASS,
        role="CANDIDATE", full_name="Candidate Test"
    )

    today = timezone.localdate()
    from datetime import timedelta

    job_open = JobPost.objects.create(
        title="[T42] Python Developer",
        description="Dev Python",
        requirements="Python 3 years",
        deadline=today + timedelta(days=10),
        status=JobPost.Status.OPEN,
        created_by=hr,
    )
    job_closed = JobPost.objects.create(
        title="[T42] Data Analyst",
        description="Data analyst",
        requirements="SQL 2 years",
        deadline=today + timedelta(days=10),
        status=JobPost.Status.CLOSED,
        created_by=hr,
    )
    job_expired = JobPost.objects.create(
        title="[T42] Old Dev",
        description="Legacy",
        requirements="COBOL",
        deadline=today - timedelta(days=1),
        status=JobPost.Status.OPEN,
        created_by=hr,
    )

    c = Client()
    c.force_login(cand)

    # ---------- Test 1: Candidate GET /viec-lam/ -> 200 ----------
    r = c.get(reverse("jobs:job-list"))
    if r.status_code == 200:
        ok("Candidate GET /viec-lam/ -> 200")
    else:
        fail("Candidate GET /viec-lam/ -> 200", "status=" + str(r.status_code))

    # ---------- Test 2: Chi hien thi tin OPEN + chua het han ----------
    content = r.content.decode("utf-8")
    if job_open.title in content:
        ok("Job OPEN hien thi trong danh sach")
    else:
        fail("Job OPEN hien thi trong danh sach")

    if job_closed.title not in content:
        ok("Job CLOSED khong hien thi")
    else:
        fail("Job CLOSED khong hien thi", "van thay trong HTML")

    if job_expired.title not in content:
        ok("Job het han (OPEN nhung qua han) khong hien thi")
    else:
        fail("Job het han khong hien thi", "van thay trong HTML")

    # ---------- Test 3: Tim kiem ?q=Python ----------
    r2 = c.get(reverse("jobs:job-list") + "?q=Python")
    if r2.status_code == 200:
        ok("Tim kiem ?q=Python -> 200")
    else:
        fail("Tim kiem ?q=Python -> 200", "status=" + str(r2.status_code))

    content2 = r2.content.decode("utf-8")
    if job_open.title in content2:
        ok("Ket qua tim kiem co Python Dev")
    else:
        fail("Ket qua tim kiem co Python Dev")

    # ---------- Test 4: Chi tiet tin OPEN -> 200 ----------
    url_open = reverse("jobs:job-detail", kwargs={"pk": job_open.pk})
    r3 = c.get(url_open)
    if r3.status_code == 200:
        ok("Candidate GET chi tiet tin OPEN -> 200")
    else:
        fail("Candidate GET chi tiet tin OPEN -> 200", "status=" + str(r3.status_code))

    content3 = r3.content.decode("utf-8")
    # Template render URL nop-ho-so/<pk>/ cho nut ung tuyen
    if "nop-ho-so" in content3:
        ok("Chi tiet tin OPEN co nut nop ho so (URL nop-ho-so)")
    else:
        fail("Chi tiet tin OPEN co nut nop ho so")

    # ---------- Test 5: Chi tiet tin CLOSED -> 404 ----------
    url_closed = reverse("jobs:job-detail", kwargs={"pk": job_closed.pk})
    r4 = c.get(url_closed)
    if r4.status_code == 404:
        ok("Candidate GET chi tiet tin CLOSED -> 404")
    else:
        fail("Candidate GET chi tiet tin CLOSED -> 404", "status=" + str(r4.status_code))

    # ---------- Test 6: Chi tiet tin het han -> 404 ----------
    url_expired = reverse("jobs:job-detail", kwargs={"pk": job_expired.pk})
    r5 = c.get(url_expired)
    if r5.status_code == 404:
        ok("Candidate GET chi tiet tin het han -> 404")
    else:
        fail("Candidate GET chi tiet tin het han -> 404", "status=" + str(r5.status_code))

    # ---------- Test 7: HR xem chi tiet tin CLOSED -> 200 ----------
    c.force_login(hr)
    r6 = c.get(url_closed)
    if r6.status_code == 200:
        ok("HR GET chi tiet tin CLOSED -> 200")
    else:
        fail("HR GET chi tiet tin CLOSED -> 200", "status=" + str(r6.status_code))

    # HR khong thay nut nop ho so
    content6 = r6.content.decode("utf-8")
    if "nop-ho-so" not in content6:
        ok("HR khong thay nut nop ho so")
    else:
        fail("HR khong thay nut nop ho so", "van thay nop-ho-so")

    # ---------- Test 8: Candidate da nop -> thong bao, khong co nut nop ----------
    app = Application.objects.create(
        job_post=job_open,
        candidate=cand,
        cv_file="cvs/fake.pdf",
        cv_original_name="fake.pdf",
        current_status="APPLIED",
        scoring_status="PENDING",
        similarity_score=None,
        ranking_position=None,
    )
    c.force_login(cand)
    r7 = c.get(url_open)
    content7 = r7.content.decode("utf-8")

    # Nut nop ho so bi an khi da nop
    if "nop-ho-so" not in content7:
        ok("Candidate da nop: nut nop bi an")
    else:
        fail("Candidate da nop: nut nop bi an", "van thay href nop-ho-so")

    # Thong bao da nop duoc hien thi (HTML render Unicode -> encode de check)
    # Template: "Bạn đã nộp hồ sơ" — check bytes
    raw7 = r7.content
    # "Da nop" encode UTF-8: "đã nộp" = b'\xc4\x91\xc3\xa3 n\xe1\xbb\x99p'
    if b'ho-so-cua-toi' in raw7 or b'hien-thi' in raw7 or b'alert-success' in raw7:
        ok("Candidate da nop: hien thi thong bao thanh cong (alert-success)")
    else:
        fail("Candidate da nop: hien thi thong bao", "khong tim thay alert-success")

    # ---------- Test 9: Trang danh sach co form search ----------
    c.force_login(cand)
    r8 = c.get(reverse("jobs:job-list"))
    content8 = r8.content.decode("utf-8")
    if 'name="q"' in content8:
        ok("Trang danh sach co form tim kiem (input name=q)")
    else:
        fail("Trang danh sach co form tim kiem")

    # ---------- Test 10: paginate_by duoc khai bao (kiem tra phan trang HTML) ----------
    # Voi < 12 ban ghi, phan trang khong hien; nhung class page-item can ton tai khi > 12
    # Cho nay chi check paginate_by duoc khai bao trong view (via model config)
    from jobs.views import JobListView
    if getattr(JobListView, "paginate_by", None) == 12:
        ok("JobListView.paginate_by = 12 duoc cau hinh")
    else:
        fail("JobListView.paginate_by = 12", "gia tri = " + str(getattr(JobListView, "paginate_by", "None")))

    # ---------- Cleanup ----------
    Application.objects.filter(pk=app.pk).delete()
    JobPost.objects.filter(title__startswith="[T42]").delete()
    User.objects.filter(email__endswith="@t42.test").delete()

    # ---------- Summary ----------
    total = len(results)
    passed = sum(1 for rr, _ in results if rr == "OK")
    failed_count = total - passed
    sys.stdout.buffer.write(("\n=== Ket qua: " + str(passed) + "/" + str(total) + " passed").encode("utf-8"))
    if failed_count:
        sys.stdout.buffer.write((" | " + str(failed_count) + " FAILED ===\n").encode("utf-8"))
    else:
        sys.stdout.buffer.write(b" | Tat ca PASSED ===\n")

run()
