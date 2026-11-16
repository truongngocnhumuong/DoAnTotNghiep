# Hướng dẫn Kiểm thử Hệ thống Tuyển dụng Nhân sự

## Yêu cầu môi trường

- Python 3.10+
- Các thư viện đã cài: Django 4.2, pdfminer.six, python-docx, scikit-learn, SortableJS (CDN), Chart.js (CDN)
- SQLite (mặc định, không cần cài thêm)

---

## 1. Khởi động hệ thống

```powershell
# Bước 1: Chuyển vào thư mục dự án
cd e:\DOANTOTNGHIEP\DOAN

# Bước 2: Tạo dữ liệu mẫu (lần đầu chạy)
python manage.py create_demo_data

# Bước 3: Khởi động server
python manage.py runserver

# Truy cập: http://127.0.0.1:8000/
```

> **Lưu ý:** Nếu muốn reset dữ liệu về trạng thái ban đầu:
> `python manage.py create_demo_data --reset`

---

## 2. Tài khoản Demo

| Vai trò | Email | Mật khẩu |
|---------|-------|-----------|
| Quản trị viên (Admin) | admin@demo.com | Admin@1234 |
| Nhân sự (HR) | hr@demo.com | Hr@1234 |
| Ứng viên 1 | candidate1@demo.com | Cand@1234 |
| Ứng viên 2 | candidate2@demo.com | Cand@1234 |
| Ứng viên 3 | candidate3@demo.com | Cand@1234 |

---

## 3. Kiểm thử theo vai trò ADMIN

**Đăng nhập:** `admin@demo.com` / `Admin@1234`

### 3.1 Quản lý tài khoản

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| A1 | Vào trang quản lý tài khoản | `/accounts/nguoi-dung/` | Danh sách tất cả người dùng, trạng thái và nút thao tác |
| A2 | Xem chi tiết tài khoản | `/accounts/nguoi-dung/<id>/` | Thấy thông tin đầy đủ: tên đăng nhập, email, vai trò, ngày tạo... |
| A3 | Khóa tài khoản | Nhấn nút "Khóa" ở danh sách hoặc chi tiết | Tài khoản bị khóa (`is_active=False`), không thể đăng nhập |
| A4 | Mở khóa tài khoản | Nhấn nút "Mở khóa" ở danh sách hoặc chi tiết | Tài khoản hoạt động lại bình thường |
| A5 | Thử tự khóa chính mình | Nhấn nút khóa ở tài khoản Admin đang login | Báo lỗi, hệ thống chặn không cho tự khóa |
| A6 | Truy cập Django Admin | `/admin/` | Panel admin Django đầy đủ (dành cho quản trị phát triển) |

### 3.2 Kiểm tra phân quyền

| # | Thao tác | Kết quả mong đợi |
|---|----------|------------------|
| A8 | Thử truy cập trang Candidate (nộp hồ sơ) | Redirect về trang 403 hoặc redirect dashboard |
| A9 | Xem danh sách hồ sơ ứng tuyển | `/applications/` | Thấy tất cả hồ sơ |

---

## 4. Kiểm thử theo vai trò HR

**Đăng nhập:** `hr@demo.com` / `Hr@1234`

### 4.1 Quản lý tin tuyển dụng

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| H1 | Xem danh sách tin (HR) | `/jobs/quan-ly/tin-tuyen-dung/` | Danh sách 3 tin (Python, UI/UX, Marketing) |
| H2 | Tạo tin tuyển dụng mới | `/jobs/quan-ly/tin-tuyen-dung/them/` | Form tạo tin, điền đầy đủ, lưu thành công |
| H3 | Chỉnh sửa tin | `/jobs/quan-ly/tin-tuyen-dung/<id>/sua/` | Sửa title/description, lưu → tính lại điểm CV |
| H4 | Đóng tin tuyển dụng | Form chỉnh sửa → chọn trạng thái "Đã đóng" | Tin chuyển sang CLOSED, ứng viên không nộp được |
| H5 | Xem chi tiết tin (HR) | `/jobs/quan-ly/tin-tuyen-dung/<id>/` | Thấy danh sách hồ sơ, điểm, thứ hạng |

### 4.2 Quản lý hồ sơ Kanban

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| H6 | Mở Kanban | `/applications/<job_id>/kanban/` | 5 cột: Đã nộp, Đang xét, Phỏng vấn, Đề nghị, Từ chối |
| H7 | Kéo thả hồ sơ | Kéo card từ "Đã nộp" → "Đang xét" | Card di chuyển, trạng thái cập nhật ngay |
| H8 | Kéo sang trạng thái không hợp lệ | Kéo từ "Đề nghị" → "Đang xét" | Thông báo lỗi, hồ sơ về vị trí cũ |
| H9 | Kéo hồ sơ "Từ chối" | Thử kéo card đã từ chối sang cột khác | Thông báo lỗi, không cho phép |
| H10 | Khôi phục hồ sơ từ chối | Vào chi tiết hồ sơ → nút "Khôi phục" | Trang xác nhận → sau đồng ý chuyển về REVIEWING |

### 4.3 Ghi chú phỏng vấn

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| H11 | Thêm ghi chú phỏng vấn | `/applications/<id>/` → form ghi chú | Điền tiêu đề + nội dung, lưu thành công |
| H12 | Xem lịch sử ghi chú | `/applications/<id>/` | Danh sách ghi chú theo thứ tự mới nhất |

### 4.4 Dashboard

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| H13 | Xem Dashboard | `/dashboard/` | Thẻ thống kê: tổng hồ sơ, điểm TB, tỷ lệ OFFERED |
| H14 | Biểu đồ trạng thái | Dashboard | Biểu đồ donut hiển thị phân bổ trạng thái |
| H15 | Top 5 tin tuyển dụng | Dashboard | Biểu đồ cột ngang top 5 tin nhiều hồ sơ nhất |

---

## 5. Kiểm thử theo vai trò CANDIDATE

**Đăng nhập:** `candidate3@demo.com` / `Cand@1234` (ứng viên chưa nộp hồ sơ nào)

### 5.1 Đăng ký tài khoản mới

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| C1 | Truy cập trang đăng ký | `/accounts/register/` | Form đăng ký có lựa chọn Vai trò: **Ứng viên** hoặc **Nhân sự (HR)** |
| C2 | Đăng ký tài khoản Ứng viên | Chọn vai trò "Ứng viên", điền đầy đủ | Thông báo thành công, đăng nhập vào có menu Ứng viên (Việc làm, Hồ sơ) |
| C2b | Đăng ký tài khoản Nhân sự | Chọn vai trò "Nhân sự / Tuyển dụng", điền đầy đủ | Thông báo thành công, đăng nhập vào có menu Nhân sự (Tin tuyển dụng, Kanban, Thống kê) |
| C3 | Đăng ký email trùng | Dùng email đã có | Thông báo lỗi "Email đã được sử dụng" |

### 5.2 Duyệt tin tuyển dụng

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| C4 | Xem danh sách tin | `/` hoặc `/viec-lam/` | Chỉ thấy tin OPEN + còn hạn |
| C5 | Xem chi tiết tin | `/viec-lam/<id>/` | Thông tin đầy đủ, nút "Nộp hồ sơ" |
| C6 | Tin đã đóng | `/viec-lam/<id>/` (tin CLOSED) | Thấy thông báo "Không còn nhận hồ sơ", ẩn nút nộp |

### 5.3 Nộp hồ sơ

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| C7 | Nộp CV hợp lệ (PDF) | `/applications/apply/<job_id>/` | Upload file PDF, submit thành công |
| C8 | Nộp CV hợp lệ (DOCX) | Nộp file DOCX | Upload thành công |
| C9 | Nộp CV quá 5MB | Upload file > 5MB | Thông báo lỗi dung lượng |
| C10 | Nộp file sai định dạng | Upload file .exe hoặc .jpg | Thông báo lỗi định dạng không hợp lệ |
| C11 | Nộp hồ sơ trùng | Nộp cùng tin 2 lần | Thông báo "Bạn đã nộp hồ sơ cho tin này" |

### 5.4 Theo dõi hồ sơ

| # | Thao tác | URL | Kết quả mong đợi |
|---|----------|-----|------------------|
| C12 | Xem hồ sơ của mình | `/applications/cua-toi/` | Chỉ thấy hồ sơ của mình, không thấy người khác |
| C13 | Xem chi tiết hồ sơ | `/applications/<id>/` | Thông tin hồ sơ, trạng thái, lịch sử |
| C14 | Xem hồ sơ người khác | Thay ID sang hồ sơ của candidate khác | Redirect 403 hoặc 404 |
| C15 | Tải lại CV | `/applications/<id>/cv/download/` | Tải về đúng file CV đã nộp |

---

## 6. Kiểm thử phân quyền biên

| # | Thao tác | Kết quả mong đợi |
|---|----------|------------------|
| P1 | Truy cập khi chưa đăng nhập vào trang cần đăng nhập | Redirect về trang đăng nhập |
| P2 | Candidate cố vào `/jobs/quan-ly/tin-tuyen-dung/` | Hiển thị trang 403 |
| P3 | HR cố vào `/accounts/users/` | Hiển thị trang 403 |
| P4 | Tài khoản bị khóa thử đăng nhập | Thông báo "Tài khoản đã bị khóa" |
| P5 | Truy cập URL không tồn tại | Hiển thị trang 404 tùy chỉnh |

---

## 7. Chạy kiểm thử tự động

```powershell
cd e:\DOANTOTNGHIEP\DOAN

# Chạy tất cả unit tests
python manage.py test accounts jobs applications --verbosity=2

# Kết quả mong đợi: Ran 28 tests in X.XXXs - OK
```

---

## 8. Kiểm tra hệ thống

```powershell
cd e:\DOANTOTNGHIEP\DOAN

# Kiểm tra cấu hình Django
python manage.py check

# Kết quả mong đợi: System check identified no issues (0 silenced).
```
