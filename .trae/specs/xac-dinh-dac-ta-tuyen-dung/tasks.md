# Tasks

- [x] Task 1: Khởi tạo Django project và cấu trúc 4 app theo đặc tả.
  - [x] SubTask 1.1: Tạo project Django và các app `accounts`, `jobs`, `applications`, `dashboard`
  - [x] SubTask 1.2: Cấu hình `settings`, `urls`, static, media, SQLite, `AUTH_USER_MODEL = "accounts.User"` trước migrate lần đầu; giữ `django.contrib.admin` tại `/admin/` cho phát triển
  - [x] SubTask 1.3: Thiết lập layout Bootstrap 5 dùng chung cho toàn hệ thống

- [x] Task 2: Xây dựng mô hình dữ liệu và migration cho 5 bảng chính.
  - [x] SubTask 2.1: Xây dựng custom user model kế thừa `AbstractUser` (`full_name`, `role`, `phone`); email bắt buộc, unique, chuẩn hóa trước khi kiểm tra trùng; không tự băm mật khẩu; không ngoại lệ demo
  - [x] SubTask 2.2: Xây dựng model `JobPost` với ForeignKey `created_by` theo quy ước Django
  - [x] SubTask 2.3: Xây dựng model `Application` gồm `scoring_status`, điểm/thứ hạng nullable, unique `(job_post, candidate)`, `current_status` gồm `APPLIED`/`REVIEWING`/`INTERVIEW`/`OFFERED`/`REJECTED`
  - [x] SubTask 2.4: Xây dựng model `ApplicationStatusHistory` với `changed_by` bắt buộc, cho phép Candidate ở bản ghi `APPLIED`
  - [x] SubTask 2.5: Xây dựng model `InterviewNote` với ForeignKey `created_by`
  - [x] SubTask 2.6: Tạo migration đầu tiên sau khi đã có `AUTH_USER_MODEL`; kiểm tra quan hệ, `on_delete`, ràng buộc dữ liệu

- [x] Task 3: Xây dựng xác thực và phân quyền theo vai trò.
  - [x] SubTask 3.1: Tạo luồng đăng ký Candidate bằng `create_user`; chuẩn hóa và unique email; thông báo thành công rồi chuyển trang đăng nhập; không tự login; không cho tự chọn `ADMIN`/`HR`
  - [x] SubTask 3.2: Tạo đăng nhập, đăng xuất bằng Django Authentication
  - [x] SubTask 3.3: Tạo decorator hoặc mixin kiểm tra vai trò `ADMIN`, `HR`, `CANDIDATE` phía máy chủ
  - [x] SubTask 3.4: Xây dựng màn hình Admin đồ án quản lý tài khoản và phân quyền đủ theo đặc tả; đăng ký Django Admin `/admin/` cho phát triển, cùng ràng buộc email/`role`
  - [x] SubTask 3.5: Kiểm tra object-level: Candidate chỉ thao tác hồ sơ của mình

- [ ] Task 4: Xây dựng chức năng quản lý tin tuyển dụng.
  - [x] SubTask 4.1: Tạo danh sách, tạo mới, chỉnh sửa và đóng tin tuyển dụng cho HR
  - [ ] SubTask 4.2: Tạo trang danh sách và chi tiết tin tuyển dụng cho Candidate
  - [ ] SubTask 4.3: Kiểm tra điều kiện tin mở tuyển và hạn nộp
  - [ ] SubTask 4.4: Khi `title`/`description`/`requirements` đổi, gọi tính lại điểm và thứ hạng của tin đó

- [ ] Task 5: Xây dựng chức năng nộp hồ sơ ứng tuyển và quản lý hồ sơ cơ bản.
  - [ ] SubTask 5.1: Tạo form upload CV cho Candidate
  - [ ] SubTask 5.2: Kiểm tra phần mở rộng, nội dung thực tế (magic/cấu trúc PDF hoặc DOCX), dung lượng tối đa 5 MB; chấp nhận `application/octet-stream` khi nội dung hợp lệ; chặn nộp trùng
  - [ ] SubTask 5.3: Lưu `Application` trạng thái `APPLIED`, `scoring_status=PENDING`, lịch sử với `changed_by` là Candidate
  - [ ] SubTask 5.4: Tạo màn hình Candidate theo dõi hồ sơ đã nộp, lọc theo `request.user`
  - [ ] SubTask 5.5: View tải CV có kiểm tra đăng nhập và quyền; không phục vụ CV qua URL media công khai

- [ ] Task 6: Xây dựng pipeline xử lý CV và chấm điểm CV-JD.
  - [ ] SubTask 6.1: Tạo service trích xuất văn bản từ PDF chỉ bằng `pdfminer.six`; không thêm `PyPDF2`
  - [ ] SubTask 6.2: Tạo service trích xuất văn bản từ DOCX bằng `python-docx`
  - [ ] SubTask 6.3: Tạo bước tiền xử lý văn bản CV và JD
  - [ ] SubTask 6.4: Fit một `TfidfVectorizer` trên corpus JD + các CV hợp lệ cùng `JobPost`, rồi tính Cosine Similarity
  - [ ] SubTask 6.5: Lưu `cv_text`, `scoring_status`, `similarity_score`, `ranking_position`; dưới 100 ký tự sau chuẩn hóa thì `INSUFFICIENT_TEXT`; không gán điểm 0 khi lỗi hoặc văn bản rỗng
  - [ ] SubTask 6.6: Tính lại toàn bộ điểm và thứ hạng của tin khi có CV mới hoặc JD đổi
  - [ ] SubTask 6.7: Hiển thị điểm, thứ hạng và trạng thái chấm trên danh sách hồ sơ

- [ ] Task 7: Xây dựng Kanban, lịch sử trạng thái và ghi chú phỏng vấn.
  - [ ] SubTask 7.1: Tạo giao diện Kanban bằng `SortableJS`
  - [ ] SubTask 7.2: Cập nhật `current_status` khi kéo thả qua view máy chủ; chỉ nhận cạnh hợp lệ; no-op nếu cùng trạng thái; từ chối kéo `REJECTED` sang trạng thái khác
  - [ ] SubTask 7.3: Lưu `ApplicationStatusHistory` với `changed_by` là HR/Admin đang đăng nhập cho mọi lần đổi trạng thái
  - [ ] SubTask 7.4: Tạo thao tác khôi phục hồ sơ `REJECTED` riêng, có xác nhận, ghi lịch sử, không dùng kéo thả
  - [ ] SubTask 7.5: Tạo chức năng thêm và xem `InterviewNote`

- [ ] Task 8: Xây dựng dashboard tuyển dụng.
  - [ ] SubTask 8.1: Tạo truy vấn tổng hợp số liệu; điểm trung bình chỉ lấy hồ sơ `SCORED` nếu có; tỷ lệ OFFERED = (số OFFERED / tổng hồ sơ) × 100% kèm chú thích ý nghĩa
  - [ ] SubTask 8.2: Hiển thị thẻ thống kê tổng quan
  - [ ] SubTask 8.3: Hiển thị biểu đồ bằng `Chart.js`

- [ ] Task 9: Xử lý lỗi, phân quyền biên và thông báo người dùng.
  - [ ] SubTask 9.1: Xử lý lỗi đăng nhập, truy cập trái quyền, tài khoản bị khóa, tải CV trái phép, email trùng sau chuẩn hóa và chuyển Kanban không hợp lệ
  - [ ] SubTask 9.2: Xử lý lỗi tệp CV, lỗi trích xuất và lỗi chấm điểm (không biến lỗi thành điểm 0)
  - [ ] SubTask 9.3: Chuẩn hóa thông báo lỗi và thông báo thành công trên giao diện

- [ ] Task 10: Kiểm thử và hoàn thiện bản demo đồ án.
  - [ ] SubTask 10.1: Viết test cho model, phân quyền object-level, corpus TF-IDF dùng chung và lịch sử `changed_by`
  - [ ] SubTask 10.2: Kiểm thử thủ công theo vai trò Admin, HR, Candidate
  - [ ] SubTask 10.3: Tạo dữ liệu mẫu phục vụ demo và chụp minh chứng cho báo cáo

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 2 and Task 3
- Task 5 depends on Task 3 and Task 4
- Task 6 depends on Task 5
- Task 7 depends on Task 5
- Task 8 depends on Task 4 and Task 5
- Task 9 depends on Task 3, Task 4, Task 5, Task 6 and Task 7
- Task 10 depends on Task 1 through Task 9
- Task 4.4 depends on service chấm điểm ở Task 6; khi lập trình có thể để hook rồi nối sau khi Task 6 xong

# Gợi ý song song hóa
- Sau khi hoàn tất Task 3, có thể triển khai song song Task 4 và một phần giao diện dùng chung của Task 8.
- Sau khi hoàn tất Task 5, có thể triển khai song song Task 6 và Task 7.
