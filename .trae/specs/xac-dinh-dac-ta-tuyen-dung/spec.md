# Đặc Tả Kỹ Thuật Hệ Thống Quy Trình Tuyển Dụng Nhân Sự

## Vì sao
Đồ án cần một đặc tả kỹ thuật đủ rõ để triển khai thành một website tuyển dụng có thể chạy thực tế trên máy tính cá nhân, dễ kiểm thử và phù hợp với phạm vi tốt nghiệp đại học. Tài liệu này thống nhất phạm vi chức năng, mô hình dữ liệu, luồng nghiệp vụ và cấu trúc Django project để làm căn cứ viết code và báo cáo.

## Những thay đổi
- Xác định đầy đủ yêu cầu chức năng cho 3 vai trò: Admin, HR/Recruiter, Candidate.
- Xác định yêu cầu phi chức năng tập trung vào bảo mật, phân quyền, kiểm tra tệp CV và khả năng vận hành trên môi trường cá nhân.
- Liệt kê danh sách màn hình chính và chức năng của từng màn hình.
- Thiết kế cơ sở dữ liệu với 5 bảng chính: `User`, `JobPost`, `Application`, `ApplicationStatusHistory`, `InterviewNote`.
- Đặc tả luồng xác thực, phân quyền, quản lý JD, nộp CV, chấm điểm CV-JD, Kanban, dashboard và xử lý lỗi.
- Đề xuất cấu trúc Django project với 4 app: `accounts`, `jobs`, `applications`, `dashboard`.
- Phân biệt rõ hạng mục bắt buộc và hạng mục tùy chọn trong phạm vi đồ án.
- Rà soát trước lập trình: custom user model và `AUTH_USER_MODEL`; quy tắc `changed_by` khi nộp hồ sơ; corpus TF-IDF dùng chung theo từng `JobPost`; tính lại điểm/thứ hạng khi có CV mới hoặc JD đổi; không gán điểm 0 cho CV lỗi; bảo vệ tệp CV và kiểm tra quyền phía máy chủ; quy ước đặt tên ForeignKey của Django.
- Chốt quyết định: email bắt buộc, unique, chuẩn hóa trước khi kiểm tra trùng, không ngoại lệ demo; CV tối đa 5 MB, chỉ PDF/DOCX, xác minh nội dung thật (kể cả `octet-stream`); Kanban 5 trạng thái kèm chuyển hợp lệ và khôi phục từ chối riêng; PDF chỉ `pdfminer.six`; sau đăng ký thông báo rồi tới trang đăng nhập; giữ `/admin/` và Admin đồ án cùng quy tắc email/`role`; ngưỡng chấm điểm 100 ký tự sau chuẩn hóa; tỷ lệ OFFERED = (số OFFERED / tổng hồ sơ) × 100%.

## Tác động
- Đặc tả bị ảnh hưởng: quản lý người dùng, tuyển dụng, chấm điểm CV-JD, theo dõi trạng thái hồ sơ, dashboard.
- Mã nguồn bị ảnh hưởng trong giai đoạn triển khai: `config/`, `accounts/`, `jobs/`, `applications/`, `dashboard/`, thư mục `templates/`, `static/`, cơ sở dữ liệu SQLite.
- `tasks.md` và `checklist.md` được đồng bộ theo các quy tắc kỹ thuật đã chốt, không mở rộng phạm vi hay thêm công nghệ mới.

## Phạm vi triển khai

### Chức năng bắt buộc
- Đăng ký, đăng nhập, đăng xuất và phân quyền theo vai trò.
- Admin quản lý tài khoản và vai trò người dùng.
- HR tạo, sửa, ẩn/đóng tin tuyển dụng.
- Candidate xem tin tuyển dụng, nộp CV và theo dõi trạng thái hồ sơ.
- Hệ thống lưu hồ sơ ứng tuyển, trích xuất nội dung CV PDF/DOCX, chấm điểm phù hợp CV-JD bằng TF-IDF và Cosine Similarity.
- HR xem danh sách ứng viên, điểm phù hợp, xếp hạng và lịch sử trạng thái.
- Quản lý trạng thái tuyển dụng theo Kanban.
- Ghi chú phỏng vấn.
- Dashboard thống kê cơ bản phục vụ theo dõi tuyển dụng.

### Chức năng tùy chọn
- Tìm kiếm và lọc nâng cao cho tin tuyển dụng.
- Phân trang danh sách lớn.
- API REST cho một số thao tác đọc dữ liệu Kanban hoặc dashboard nếu giao diện yêu cầu cập nhật bất đồng bộ.
- Xuất báo cáo thống kê ra tệp.

### Ngoài phạm vi
- Tích hợp email doanh nghiệp, SMS, chatbot, OCR nâng cao hoặc AI sinh ngôn ngữ.
- Tích hợp lịch ngoài hệ thống, phỏng vấn trực tuyến, nhiều chi nhánh hoặc quy trình phê duyệt nhiều tầng.
- Thuật toán xếp hạng phức tạp ngoài TF-IDF và Cosine Similarity.
- Thư viện đọc PDF khác ngoài `pdfminer.six` (không dùng `PyPDF2` ở phiên bản đầu).

### Công nghệ đã chốt
- Python, Django, SQLite.
- HTML, CSS, Bootstrap 5.
- Django Authentication; custom user kế thừa `AbstractUser`.
- scikit-learn: TF-IDF và Cosine Similarity.
- `pdfminer.six` cho PDF; `python-docx` cho DOCX.
- SortableJS và Chart.js.
- Django REST Framework chỉ khi thật sự cần.
- `django.contrib.admin` tại `/admin/` dùng khi phát triển và kiểm tra dữ liệu, không bắt buộc trong buổi demo.

## 1. Yêu cầu chức năng theo vai trò

## ADDED Requirements

### Requirement: Admin quản lý tài khoản và phân quyền
Hệ thống SHALL cho phép Admin quản lý tài khoản người dùng và gán vai trò `ADMIN`, `HR`, `CANDIDATE`.

#### Scenario: Admin tạo tài khoản HR
- **WHEN** Admin nhập thông tin người dùng hợp lệ trên giao diện Admin của đồ án và chọn vai trò `HR`
- **THEN** hệ thống chuẩn hóa email, kiểm tra trùng phía máy chủ, tạo tài khoản mới và tài khoản đó có quyền truy cập các màn hình HR

#### Scenario: Email trùng sau khi chuẩn hóa
- **WHEN** Admin hoặc form đăng ký gửi email chỉ khác hoa/thường hoặc khoảng trắng so với email đã có
- **THEN** hệ thống từ chối lưu vì vi phạm unique; không có ngoại lệ cho tài khoản demo hay seed

#### Scenario: Admin khóa tài khoản
- **WHEN** Admin đổi trạng thái tài khoản sang không hoạt động
- **THEN** người dùng đó không thể đăng nhập vào hệ thống

### Requirement: HR quản lý tin tuyển dụng
Hệ thống SHALL cho phép HR tạo, cập nhật, xem chi tiết, ẩn hoặc đóng tin tuyển dụng.

#### Scenario: HR tạo tin tuyển dụng
- **WHEN** HR nhập đầy đủ tiêu đề, mô tả công việc, yêu cầu, hạn nộp và trạng thái mở tuyển
- **THEN** hệ thống lưu tin và Candidate có thể xem tin đó trên danh sách tuyển dụng

#### Scenario: HR đóng tin tuyển dụng
- **WHEN** HR đổi trạng thái tin sang đóng
- **THEN** Candidate không thể nộp hồ sơ mới vào tin đó

### Requirement: HR tiếp nhận và xử lý hồ sơ ứng tuyển
Hệ thống SHALL cho phép HR xem danh sách hồ sơ, xem CV, điểm phù hợp CV-JD, thứ hạng, trạng thái và lịch sử xử lý.

#### Scenario: HR xem danh sách ứng viên theo tin tuyển dụng
- **WHEN** HR mở màn hình chi tiết tin tuyển dụng
- **THEN** hệ thống hiển thị toàn bộ hồ sơ ứng tuyển thuộc tin đó kèm điểm và trạng thái hiện tại

### Requirement: Candidate ứng tuyển và theo dõi hồ sơ
Hệ thống SHALL cho phép Candidate xem tin tuyển dụng, nộp CV và theo dõi trạng thái xử lý hồ sơ của chính mình.

#### Scenario: Candidate nộp hồ sơ hợp lệ
- **WHEN** Candidate chọn một tin đang mở và tải lên CV đúng định dạng được hỗ trợ
- **THEN** hệ thống tạo bản ghi ứng tuyển, lưu tệp CV, gắn trạng thái `APPLIED`, ghi lịch sử với `changed_by` là chính Candidate đó, rồi đưa hồ sơ vào pipeline trích xuất và chấm điểm

#### Scenario: Candidate xem trạng thái hồ sơ
- **WHEN** Candidate truy cập danh sách hồ sơ đã nộp
- **THEN** hệ thống chỉ trả về các hồ sơ thuộc chính Candidate đó sau khi kiểm tra quyền phía máy chủ; không dựa vào việc ẩn liên kết trên giao diện

## 2. Yêu cầu phi chức năng

### Requirement: Bảo mật xác thực và phân quyền
Hệ thống SHALL dùng Django Authentication và custom user model kế thừa `AbstractUser`. Mật khẩu SHALL được băm bằng cơ chế có sẵn của Django (`set_password`, `create_user`, `authenticate`). Hệ thống SHALL NOT tự viết hàm băm mật khẩu, tự so khớp mật khẩu thô, hay tự triển khai session login ngoài Django.

Mọi view nghiệp vụ SHALL kiểm tra đăng nhập và vai trò phía máy chủ bằng mixin/decorator hoặc tương đương. Ẩn nút trên giao diện không đủ để coi là phân quyền.

#### Scenario: Người dùng không đúng vai trò truy cập URL HR
- **WHEN** Candidate truy cập trực tiếp URL quản trị tuyển dụng
- **THEN** hệ thống từ chối truy cập ở phía máy chủ và trả về điều hướng phù hợp hoặc thông báo không có quyền

#### Scenario: Candidate truy cập hồ sơ người khác
- **WHEN** Candidate đã đăng nhập gọi URL chi tiết hoặc tải CV của hồ sơ không thuộc mình
- **THEN** hệ thống trả về 403 hoặc 404; không trả nội dung hồ sơ hay tệp CV

### Requirement: Kiểm tra tệp CV
Hệ thống SHALL chỉ chấp nhận CV định dạng `pdf` hoặc `docx`, giới hạn dung lượng tối đa `5 MB`. Phía máy chủ MUST kiểm tra: phần mở rộng, nội dung thực tế của tệp, và dung lượng. Hệ thống SHALL NOT chỉ tin `content_type` do trình duyệt gửi.

Thứ tự kiểm tra khi tải lên:
1. Dung lượng ≤ 5 MB.
2. Phần mở rộng là `.pdf` hoặc `.docx` (không phân biệt hoa thường).
3. Đọc magic byte / cấu trúc tệp:
   - PDF: bắt đầu bằng `%PDF`.
   - DOCX: tệp ZIP hợp lệ (magic `PK`) và có dấu hiệu gói Office Open XML (ví dụ `[Content_Types].xml` và `word/`).
4. `content_type`:
   - PDF: chấp nhận `application/pdf`.
   - DOCX: chấp nhận `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
   - `application/octet-stream` (và tương đương rỗng/không rõ): vẫn chấp nhận nếu bước 2 và 3 đã xác minh đúng loại tệp.
   - MIME khác, hoặc MIME lệch loại so với phần mở rộng/nội dung: từ chối.

Tệp lỗi, rỗng, giả mạo phần mở rộng, hoặc không trích xuất được văn bản SHALL nhận `scoring_status` phù hợp; SHALL NOT tự gán `similarity_score = 0`.

Đường dẫn lưu tệp không được dùng tên gốc làm tên file trên đĩa. Tên gốc chỉ lưu ở `cv_original_name` để hiển thị.

#### Scenario: Candidate tải lên tệp không hợp lệ
- **WHEN** Candidate tải lên tệp sai phần mở rộng, nội dung không phải PDF/DOCX thật, MIME lệch loại, hoặc vượt `5 MB`
- **THEN** hệ thống từ chối lưu và hiển thị lỗi rõ ràng

#### Scenario: Trình duyệt gửi octet-stream
- **WHEN** Candidate tải lên tệp `.pdf` hoặc `.docx` hợp lệ nhưng `content_type` là `application/octet-stream`
- **THEN** hệ thống vẫn lưu nếu dung lượng ≤ 5 MB và nội dung thực tế khớp loại tệp

#### Scenario: CV không trích xuất được văn bản
- **WHEN** tệp đúng định dạng và dung lượng nhưng không đọc được chữ, rỗng, hoặc dưới ngưỡng văn bản
- **THEN** hồ sơ vẫn được lưu với trạng thái ứng tuyển `APPLIED`, `scoring_status` là `EXTRACTION_FAILED` hoặc `INSUFFICIENT_TEXT`, `similarity_score` và `ranking_position` để NULL

### Requirement: Bảo vệ tệp CV khi tải xuống
Hệ thống SHALL không để URL media công khai cho phép người lạ hoặc Candidate khác tải CV. Việc xem/tải CV SHALL đi qua view đã đăng nhập và kiểm tra quyền:

- Candidate: chỉ hồ sơ của chính mình.
- HR và Admin: được xem CV của hồ sơ trong hệ thống.

#### Scenario: Truy cập trực tiếp tệp CV khi chưa đủ quyền
- **WHEN** người chưa đăng nhập hoặc sai quyền gọi URL tải CV
- **THEN** hệ thống từ chối và không phát nội dung tệp

### Requirement: Khả năng chạy trên máy tính cá nhân
Hệ thống SHALL vận hành được trên một máy đơn với Python, Django và SQLite mà không phụ thuộc hạ tầng ngoài phạm vi đồ án.

#### Scenario: Chạy hệ thống cục bộ
- **WHEN** môi trường cài đủ thư viện và chạy migration
- **THEN** hệ thống có thể khởi động và dùng thử bằng dữ liệu mẫu trên máy cá nhân

### Requirement: Dễ kiểm thử và bảo trì
Hệ thống SHALL được tổ chức theo app Django rõ ràng, có lớp model, view, template và service tách biệt đủ để kiểm thử chức năng chính.

## 3. Danh sách màn hình và chức năng

### Nhóm màn hình dùng chung
- `Đăng ký`: dành cho Candidate tự tạo tài khoản; nhập thông tin cơ bản, tên đăng nhập, email, mật khẩu. Thành công thì thông báo và chuyển tới `Đăng nhập`; không tự login.
- `Đăng nhập`: xác thực người dùng theo tài khoản đã có.
- `Đổi mật khẩu` hoặc `cập nhật hồ sơ cá nhân` là tùy chọn nếu còn thời gian.

### Nhóm màn hình Admin
- `Quản lý người dùng`: danh sách tài khoản, tìm kiếm cơ bản, tạo mới, chỉnh sửa vai trò, khóa/mở tài khoản.
- `Chi tiết người dùng`: xem thông tin tài khoản và lịch sử thay đổi cơ bản nếu cần.

### Nhóm màn hình HR/Recruiter
- `Danh sách tin tuyển dụng`: xem tất cả tin do hệ thống quản lý, lọc theo trạng thái.
- `Tạo/Sửa tin tuyển dụng`: nhập tiêu đề, mô tả, yêu cầu, hạn nộp, trạng thái.
- `Chi tiết tin tuyển dụng`: xem thông tin JD, số lượng ứng viên, danh sách hồ sơ.
- `Danh sách ứng viên theo tin`: hiển thị candidate, tệp CV, điểm phù hợp, xếp hạng, trạng thái hiện tại; hồ sơ chưa chấm được phải hiển thị trạng thái xử lý, không hiện điểm 0 giả.
- `Chi tiết hồ sơ ứng tuyển`: thông tin ứng viên, nội dung CV đã trích xuất, điểm CV-JD, lịch sử trạng thái, ghi chú phỏng vấn.
- `Kanban tuyển dụng`: kéo thả hồ sơ giữa các cột `APPLIED`, `REVIEWING`, `INTERVIEW`, `OFFERED`, `REJECTED` bằng SortableJS; chỉ nhận chuyển hợp lệ; khôi phục hồ sơ `REJECTED` là thao tác riêng có xác nhận, không phải kéo thả thông thường.
- `Dashboard`: biểu đồ và số liệu tổng quan tuyển dụng.

### Nhóm màn hình Candidate
- `Trang chủ/Danh sách tin tuyển dụng`: xem các vị trí đang mở.
- `Chi tiết tin tuyển dụng`: xem JD chi tiết, điều kiện ứng tuyển, nút nộp CV.
- `Nộp hồ sơ`: chọn tệp CV và gửi hồ sơ.
- `Theo dõi hồ sơ đã nộp`: xem danh sách hồ sơ của bản thân, trạng thái hiện tại và thời gian cập nhật gần nhất.

## 4. Thiết kế cơ sở dữ liệu

### Nguyên tắc chung
- Sử dụng `SQLite`.
- Kiểu khóa chính dùng `BigAutoField` theo mặc định Django.
- Các trường thời gian dùng `DateTimeField`.
- Trạng thái dùng `CharField` với `choices`.
- Không tách quá nhiều bảng phụ ngoài phạm vi 5 bảng yêu cầu.
- ForeignKey trên model Django đặt tên theo đối tượng quan hệ, không gắn hậu tố `_id`. Django tự tạo cột CSDL `..._id`. Ví dụ trường model là `created_by`, cột CSDL là `created_by_id`.
- Mọi ForeignKey trỏ user dùng `settings.AUTH_USER_MODEL`, không import cứng model `User` vòng từ app khác nếu có thể tránh.
- `on_delete` phải được chỉ định rõ cho từng quan hệ.

### Custom user model và AUTH_USER_MODEL
- Model `User` đặt trong app `accounts`, kế thừa `django.contrib.auth.models.AbstractUser`.
- Không tạo model user độc lập ngoài hệ thống auth của Django.
- Trong `config/settings.py` phải có:

```python
AUTH_USER_MODEL = "accounts.User"
```

- `AUTH_USER_MODEL` MUST được cấu hình trước lần `migrate` đầu tiên. Không được chạy migration mặc định với `auth.User` rồi mới đổi sang custom user.
- Dùng các trường sẵn có của `AbstractUser` cho xác thực: `username`, `password`, `email`, `is_active`, `date_joined`, `last_login`, `is_staff`, `is_superuser`.
- Thêm trường nghiệp vụ: `full_name`, `role`, `phone`.
- Tạo user chỉ qua `User.objects.create_user(...)`, `create_superuser(...)` hoặc `user.set_password(...)`. Không gán chuỗi mật khẩu thô vào `user.password`.
- Vai trò nghiệp vụ dùng trường `role`. Không dùng `is_superuser` thay cho `ADMIN` trên các màn hình đồ án.
- Giữ `django.contrib.admin` tại `/admin/` để phát triển và kiểm tra dữ liệu. `/admin/` không bắt buộc trình diễn trong bản demo. Giao diện Admin của đồ án (role `ADMIN`) MUST đủ quản lý tài khoản và phân quyền.
- Tài khoản dùng `/admin/` cần `is_staff`. `is_staff` không thay thế `role = ADMIN` trên website đồ án. Form User trên `/admin/` MUST dùng cùng quy tắc email, mật khẩu Django và `role` bắt buộc; không để `/admin/` tạo user phá ràng buộc.

### Bảng `User`
Mục đích: lưu tài khoản và vai trò người dùng. Triển khai bằng custom user kế thừa `AbstractUser`.

| Trường | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | BigAutoField | PK |
| `username` | CharField(150) | Unique, Not Null; trường đăng nhập mặc định của AbstractUser |
| `email` | EmailField(254) | Unique, Not Null; chuẩn hóa trước khi lưu và trước khi kiểm tra trùng |
| `password` | CharField(128) | Not Null; hash do Django quản lý, không tự băm |
| `full_name` | CharField(150) | Not Null |
| `role` | CharField(20) | Not Null, choices: `ADMIN`, `HR`, `CANDIDATE` |
| `phone` | CharField(20) | Null, Blank |
| `is_active` | BooleanField | Default True |
| `date_joined` | DateTimeField | Default current time |
| `last_login` | DateTimeField | Null, Blank |

Quan hệ (tên trường model):
- `User (1) - (N) JobPost` qua `JobPost.created_by`.
- `User (1) - (N) Application` qua `Application.candidate`.
- `User (1) - (N) ApplicationStatusHistory` qua `ApplicationStatusHistory.changed_by`.
- `User (1) - (N) InterviewNote` qua `InterviewNote.created_by`.

`related_name` đề xuất: `job_posts`, `applications`, `status_changes`, `interview_notes`.

Chuẩn hóa email (áp dụng đăng ký, Admin đồ án, `/admin/`, seed; không ngoại lệ demo):
- Cắt khoảng trắng hai đầu.
- Chuyển về chữ thường.
- Kiểm tra định dạng hợp lệ rồi mới kiểm tra unique trên giá trị đã chuẩn hóa.
- Ràng buộc unique trên cột `email` ở CSDL. Trùng sau chuẩn hóa (ví dụ `A@Mail.com` và `a@mail.com`) MUST bị từ chối.

### Bảng `JobPost`
Mục đích: lưu tin tuyển dụng và JD.

| Trường | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | BigAutoField | PK |
| `title` | CharField(200) | Not Null |
| `department` | CharField(100) | Null, Blank |
| `location` | CharField(150) | Null, Blank |
| `employment_type` | CharField(50) | Null, Blank |
| `description` | TextField | Not Null |
| `requirements` | TextField | Not Null |
| `benefits` | TextField | Null, Blank |
| `deadline` | DateField | Not Null |
| `status` | CharField(20) | Not Null, choices: `DRAFT`, `OPEN`, `CLOSED` |
| `created_by` | ForeignKey(User) | Not Null, `on_delete=PROTECT`, chỉ nhận user `role` `HR` hoặc `ADMIN` |
| `created_at` | DateTimeField | Auto now add |
| `updated_at` | DateTimeField | Auto now |

Quan hệ:
- `JobPost (1) - (N) Application` qua `Application.job_post`.

Văn bản JD dùng để chấm điểm là chuỗi ghép `title`, `description` và `requirements` sau khi chuẩn hóa. Khi một trong các trường này thay đổi trên tin đã có hồ sơ, hệ thống MUST tính lại điểm và thứ hạng cho toàn bộ hồ sơ thuộc tin đó.

### Bảng `Application`
Mục đích: lưu hồ sơ ứng tuyển, tệp CV, kết quả chấm điểm và trạng thái hiện tại.

| Trường | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | BigAutoField | PK |
| `job_post` | ForeignKey(JobPost) | Not Null, `on_delete=CASCADE` |
| `candidate` | ForeignKey(User) | Not Null, `on_delete=PROTECT`, chỉ nhận user `role` `CANDIDATE` |
| `cv_file` | FileField | Not Null, chỉ `.pdf` hoặc `.docx`, tối đa 5 MB |
| `cv_original_name` | CharField(255) | Not Null |
| `cv_text` | TextField | Null, Blank; nội dung trích xuất thành công |
| `scoring_status` | CharField(30) | Not Null, choices: `PENDING`, `SCORED`, `EXTRACTION_FAILED`, `INSUFFICIENT_TEXT`, `SCORING_FAILED`; mặc định `PENDING` |
| `similarity_score` | FloatField | Null, Blank; chỉ có giá trị khi `scoring_status = SCORED`; khoảng 0 đến 1 |
| `ranking_position` | IntegerField | Null, Blank; chỉ gán cho hồ sơ `SCORED` |
| `current_status` | CharField(30) | Not Null, choices: `APPLIED`, `REVIEWING`, `INTERVIEW`, `OFFERED`, `REJECTED`; mặc định `APPLIED` |
| `applied_at` | DateTimeField | Auto now add |
| `updated_at` | DateTimeField | Auto now |

Ràng buộc:
- Unique theo cặp `job_post` và `candidate` (`UniqueConstraint`) để tránh nộp trùng cho cùng một tin.
- Chỉ cho phép nộp khi `JobPost.status = OPEN` và `deadline` chưa qua (so với ngày hiện tại).
- `similarity_score` nếu khác NULL thì phải thuộc `[0, 1]`.
- `similarity_score` MUST NOT được gán `0` (hoặc bất kỳ số nào) khi trích xuất thất bại, văn bản rỗng, hoặc chấm điểm lỗi. Các trường hợp đó để `similarity_score = NULL`, `ranking_position = NULL`, và `scoring_status` tương ứng.
- Candidate của bản ghi MUST là chính user đang đăng nhập khi nộp; không cho nộp hộ.

Quan hệ:
- `Application (1) - (N) ApplicationStatusHistory` qua `ApplicationStatusHistory.application`.
- `Application (1) - (N) InterviewNote` qua `InterviewNote.application`.

### Bảng `ApplicationStatusHistory`
Mục đích: lưu toàn bộ lịch sử thay đổi trạng thái hồ sơ, kể cả lần ghi nhận `APPLIED` khi nộp.

| Trường | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | BigAutoField | PK |
| `application` | ForeignKey(Application) | Not Null, `on_delete=CASCADE` |
| `from_status` | CharField(30) | Null, Blank; NULL khi là bản ghi khởi tạo lúc nộp |
| `to_status` | CharField(30) | Not Null, thuộc tập trạng thái hợp lệ |
| `changed_by` | ForeignKey(User) | Not Null, `on_delete=PROTECT`; luôn là user thật sự thực hiện thao tác |
| `note` | TextField | Null, Blank |
| `changed_at` | DateTimeField | Auto now add |

Ràng buộc `changed_by`:
- Không giới hạn chỉ `HR`/`ADMIN`. Bản ghi đầu tiên khi Candidate nộp hồ sơ có `changed_by` là Candidate đó, `from_status = NULL`, `to_status = APPLIED`.
- Khi HR hoặc Admin đổi trạng thái (Kanban hoặc form), `changed_by` MUST là tài khoản đang đăng nhập thực hiện thao tác, không lấy mặc định admin, không để trống, không ghi nhầm thành Candidate.
- Không dùng user giả lập “system” và không để `changed_by` nullable để né trường hợp nộp hồ sơ.
- Candidate chỉ được xuất hiện ở `changed_by` cho sự kiện nộp hồ sơ; Candidate không được tự đổi trạng thái sau khi nộp.

Ràng buộc trạng thái:
- Mỗi lần `current_status` đổi MUST tạo đúng một bản ghi lịch sử mới trong cùng giao dịch.
- `from_status` MUST bằng `current_status` trước khi đổi; `to_status` MUST thuộc tập và cạnh chuyển được phép của đúng loại thao tác.
- Nếu kéo thả về đúng trạng thái hiện tại: không cập nhật, không tạo lịch sử.
- Tập giá trị: `APPLIED`, `REVIEWING`, `INTERVIEW`, `OFFERED`, `REJECTED`.
- Tính hợp lệ MUST được kiểm tra phía máy chủ. Giao diện chỉ hỗ trợ; không đủ để coi là đã chặn chuyển trái phép.
- Chuyển trạng thái sau khi nộp chỉ HR và Admin.

### Bảng `InterviewNote`
Mục đích: lưu ghi chú phỏng vấn hoặc nhận xét của HR cho từng hồ sơ.

| Trường | Kiểu dữ liệu | Ràng buộc |
|---|---|---|
| `id` | BigAutoField | PK |
| `application` | ForeignKey(Application) | Not Null, `on_delete=CASCADE` |
| `created_by` | ForeignKey(User) | Not Null, `on_delete=PROTECT`, chỉ nhận user `role` `HR` hoặc `ADMIN` |
| `title` | CharField(200) | Not Null |
| `content` | TextField | Not Null |
| `interview_round` | CharField(50) | Null, Blank |
| `created_at` | DateTimeField | Auto now add |
| `updated_at` | DateTimeField | Auto now |

Chỉ HR và Admin được tạo/xem ghi chú. Candidate không xem `InterviewNote`.

## 5. Quan hệ tổng thể giữa các bảng

- Một `User` có thể tạo nhiều `JobPost`.
- Một `User` có vai trò Candidate có thể tạo nhiều `Application`.
- Một `JobPost` có nhiều `Application`.
- Một `Application` có nhiều `ApplicationStatusHistory`.
- Một `Application` có nhiều `InterviewNote`.

Ràng buộc nghiệp vụ chính:
- Chỉ `HR` và `ADMIN` được thao tác với `JobPost`, Kanban, điểm CV-JD, ghi chú phỏng vấn. Kiểm tra trên view/service, không chỉ trên template.
- Chỉ `CANDIDATE` được nộp hồ sơ cho chính mình.
- Candidate chỉ xem được `Application` của chính họ, kể cả khi đoán URL theo `id`.
- Query danh sách hồ sơ của Candidate MUST lọc `candidate=request.user` phía máy chủ.
- Query danh sách/chi tiết hồ sơ của HR/Admin MUST kiểm tra vai trò trước khi trả dữ liệu.

## 6. Đặc tả luồng đăng ký, đăng nhập, phân quyền, quản lý JD và nộp CV

### Luồng đăng ký
1. Candidate mở trang đăng ký.
2. Nhập `username`, `email`, `full_name`, `password`, `confirm_password`.
3. Hệ thống chuẩn hóa email, kiểm tra dữ liệu bắt buộc phía máy chủ, email và tên đăng nhập không trùng (theo email đã chuẩn hóa), mật khẩu đủ điều kiện tối thiểu của Django.
4. Hệ thống tạo tài khoản bằng `create_user` với `role = CANDIDATE`, `is_active = True`. Không gán `ADMIN` hoặc `HR` từ form đăng ký công khai. Không bỏ qua unique email cho bất kỳ tài khoản nào.
5. Sau đăng ký thành công: hiển thị thông báo thành công, điều hướng sang trang đăng nhập. Không gọi `login()`, không tạo session đăng nhập sẵn.

### Luồng đăng nhập
1. Người dùng nhập thông tin đăng nhập.
2. Django Authentication xác thực (`authenticate` + `login`).
3. Nếu hợp lệ và `is_active = True`, hệ thống tạo session.
4. Nếu `is_active = False`, từ chối đăng nhập.
5. Điều hướng theo vai trò:
   - `ADMIN` tới quản lý người dùng.
   - `HR` tới dashboard hoặc danh sách tin tuyển dụng.
   - `CANDIDATE` tới danh sách việc làm.

### Luồng phân quyền
1. Mỗi view kiểm tra người dùng đã đăng nhập (`LoginRequiredMixin` hoặc tương đương).
2. Kiểm tra `role` trước khi truy cập chức năng (decorator/mixin theo vai trò).
3. View chi tiết hồ sơ, tải CV, sửa JD, Kanban, ghi chú MUST kiểm tra object-level: đúng vai trò và, với Candidate, đúng chủ sở hữu.
4. Nếu không đủ quyền, trả về trang lỗi quyền hạn hoặc chuyển hướng an toàn, không lộ dữ liệu.

### Luồng quản lý JD
1. HR tạo tin tuyển dụng mới.
2. Nhập nội dung mô tả công việc và yêu cầu tuyển dụng.
3. Hệ thống lưu `JobPost` với `created_by = request.user`.
4. Khi HR sửa JD, hệ thống cập nhật nội dung và `updated_at`.
5. Nếu `title`, `description` hoặc `requirements` thay đổi và tin đã có hồ sơ: MUST chạy lại pipeline chấm điểm theo corpus dùng chung của tin đó, rồi cập nhật thứ hạng.
6. Candidate chỉ nhìn thấy tin `status = OPEN` và chưa hết hạn.

### Luồng nộp CV
1. Candidate vào chi tiết tin tuyển dụng đang mở.
2. Chọn tệp CV hợp lệ.
3. Hệ thống kiểm tra phía máy chủ:
   - đã đăng nhập,
   - đúng vai trò Candidate,
   - tin tuyển dụng còn `OPEN`,
   - chưa quá hạn,
   - chưa nộp trùng,
   - dung lượng ≤ 5 MB,
   - phần mở rộng `pdf`/`docx`,
   - nội dung thực tế là PDF hoặc DOCX hợp lệ,
   - `content_type` khớp loại tệp, hoặc là `application/octet-stream` khi nội dung đã được xác minh.
4. Hệ thống lưu `Application` với `current_status = APPLIED`, `scoring_status = PENDING`, `similarity_score = NULL`, `ranking_position = NULL`, `candidate = request.user`.
5. Trong cùng luồng lưu hồ sơ, tạo bản ghi `ApplicationStatusHistory` đầu tiên: `from_status = NULL`, `to_status = APPLIED`, `changed_by = request.user` (Candidate).
6. Gọi luồng trích xuất và chấm điểm theo corpus của `JobPost`.

## 7. Đặc tả luồng trích xuất văn bản CV, tiền xử lý, TF-IDF, Cosine Similarity, lưu điểm và xếp hạng

### Mục tiêu
Đưa ra điểm phù hợp giữa CV và JD để hỗ trợ HR sàng lọc hồ sơ ban đầu, không thay thế hoàn toàn quyết định tuyển dụng.

Điểm của các ứng viên cùng một `JobPost` MUST so sánh được với nhau vì được tính trên cùng một bộ biểu diễn TF-IDF. Không fit vectorizer riêng cho từng cặp JD–CV rồi xếp hạng như thể các điểm đó cùng thang đo.

### Bước 1: Trích xuất văn bản CV
- PDF: chỉ dùng `pdfminer.six`. Không thêm `PyPDF2` hay thư viện PDF khác ở phiên bản đầu.
- DOCX: dùng `python-docx`.
- Nếu không trích xuất được: `scoring_status = EXTRACTION_FAILED`, `cv_text` để trống, không gán điểm.
- Nếu sau chuẩn hóa văn bản rỗng hoặc ngắn hơn ngưỡng tối thiểu **100 ký tự**: `scoring_status = INSUFFICIENT_TEXT`, không gán điểm. Ngưỡng này áp dụng cho văn bản CV/JD dùng để chấm điểm, không phải độ dài trường email.
- HR nhìn thấy trạng thái lỗi rõ ràng, không thấy điểm `0.00` như đã chấm thành công.

### Bước 2: Chuẩn hóa văn bản
Áp dụng cho cả nội dung CV và JD:
- Chuyển về chữ thường.
- Loại bỏ khoảng trắng dư thừa.
- Loại bỏ ký tự đặc biệt không cần thiết.
- Có thể loại bỏ stop words tiếng Anh ở mức đơn giản nếu không làm tăng độ phức tạp quá mức.

### Bước 3: Tạo biểu diễn TF-IDF dùng chung theo JobPost
Với một `JobPost`, xây corpus gồm:
1. Một tài liệu JD: văn bản đã chuẩn hóa của tin đó.
2. Toàn bộ CV thuộc tin đó có `cv_text` hợp lệ (đã trích xuất, đủ ngưỡng). Hồ sơ `EXTRACTION_FAILED` hoặc `INSUFFICIENT_TEXT` không đưa vào corpus.

Quy tắc:
- Fit đúng một `TfidfVectorizer` trên corpus đó.
- Transform JD và từng CV bằng cùng vectorizer đã fit.
- Không fit lại từng cặp `(JD, CV_i)` độc lập khi đang xếp hạng cùng một tin.
- Nếu corpus không có CV hợp lệ nào: không fit, không ghi điểm giả; các hồ sơ giữ trạng thái lỗi/pending tương ứng.

### Bước 4: Tính Cosine Similarity
- Dùng `cosine_similarity` giữa vector JD và vector từng CV trong cùng ma trận.
- Kết quả là số thực trong `[0, 1]`.
- Điểm này mới được coi là cùng thang để xếp hạng trong tin.

### Bước 5: Lưu điểm
- Ghi `cv_text` khi trích xuất thành công.
- Chỉ khi tính similarity thành công: `similarity_score` = giá trị cosine, `scoring_status = SCORED`.
- Nếu lỗi thư viện hoặc vector rỗng sau khi đã có văn bản: `scoring_status = SCORING_FAILED`, `similarity_score = NULL`, `ranking_position = NULL`.
- Không dùng `0` làm giá trị mặc định cho thất bại.

### Bước 6: Xếp hạng ứng viên
- Chỉ xếp hạng các `Application` của cùng `JobPost` có `scoring_status = SCORED` và `similarity_score` khác NULL.
- Sắp xếp giảm dần theo `similarity_score`; nếu bằng nhau, ưu tiên `applied_at` sớm hơn, rồi `id` nhỏ hơn.
- Gán `ranking_position` bắt đầu từ 1 cho nhóm đã chấm.
- Hồ sơ chưa chấm hoặc chấm lỗi: `ranking_position = NULL`, không chen vào thứ hạng như điểm 0.

### Bước 7: Tính lại khi dữ liệu thay đổi
MUST tính lại điểm và thứ hạng của toàn bộ hồ sơ thuộc một `JobPost` (fit lại corpus dùng chung) khi:
- Có hồ sơ mới nộp và trích xuất được (hoặc thất bại: vẫn xếp hạng lại nhóm đã `SCORED`, vì thứ hạng tương đối có thể không đổi nhưng phải nhất quán).
- Có hồ sơ mới được trích xuất thành công sau lần xử lý trước.
- Nội dung JD dùng để chấm (`title`, `description`, `requirements`) thay đổi.

Cách làm:
1. Lấy toàn bộ hồ sơ của tin.
2. Trích xuất lại chỉ khi `cv_text` chưa có và tệp vẫn tồn tại; không tự coi lỗi cũ là điểm 0.
3. Fit lại một vectorizer trên JD + các CV hợp lệ hiện có.
4. Cập nhật `similarity_score` / `scoring_status` cho từng hồ sơ hợp lệ.
5. Gán lại `ranking_position` cho nhóm `SCORED`.

Nút “chấm lại” thủ công của HR là bổ sung tùy chọn, không thay thế việc tính lại bắt buộc ở trên.

### Yêu cầu bắt buộc
- Điểm chỉ được ghi khi chấm thành công.
- HR xem được điểm, thứ hạng và trạng thái chấm trên danh sách ứng viên.
- Các ứng viên cùng tin được chấm trên cùng corpus TF-IDF tại một lần tính hạng.

### Yêu cầu tùy chọn
- Cho phép HR bấm nút chấm lại toàn bộ một tin.
- Hiển thị phần từ khóa nổi bật từ CV và JD nếu còn thời gian.

## 8. Đặc tả Kanban, lịch sử thay đổi trạng thái và ghi chú phỏng vấn

### Mô hình trạng thái
- `APPLIED`: mới nộp.
- `REVIEWING`: HR đang xem xét hồ sơ.
- `INTERVIEW`: đã vào vòng phỏng vấn.
- `OFFERED`: đã đưa đề nghị nhận việc.
- `REJECTED`: không đạt / từ chối.

### Chuyển trạng thái hợp lệ

Hai loại thao tác tách biệt. Máy chủ MUST phân biệt endpoint Kanban/form thường và endpoint khôi phục.

**A. Thao tác thông thường (kéo thả Kanban hoặc đổi trạng thái trên form hồ sơ)**

| Từ | Tới được phép |
|---|---|
| `APPLIED` | `REVIEWING`, `REJECTED` |
| `REVIEWING` | `APPLIED`, `INTERVIEW`, `REJECTED` |
| `INTERVIEW` | `REVIEWING`, `OFFERED`, `REJECTED` |
| `OFFERED` | `REJECTED` |
| `REJECTED` | không có |

Quy tắc:
- Không cho phép kéo `REJECTED` sang `INTERVIEW` hay bất kỳ cột nào khác bằng thao tác thông thường.
- Không cho phép `OFFERED` → `INTERVIEW` bằng kéo thả.
- Cùng trạng thái: no-op, không ghi lịch sử.
- Chuyển không nằm bảng trên: máy chủ từ chối, không đổi `current_status`, không ghi lịch sử; giao diện hoàn thẻ về cột cũ.

**B. Khôi phục hồ sơ từ chối nhầm (thao tác riêng)**
- Chỉ khi `current_status = REJECTED`.
- Chỉ HR hoặc Admin.
- Giao diện: nút/hành động riêng trên chi tiết hồ sơ hoặc Kanban, có bước xác nhận rõ (không dùng kéo thả).
- Trạng thái đích mặc định: trạng thái ngay trước lần chuyển sang `REJECTED` gần nhất (lấy `from_status` của bản ghi lịch sử vào `REJECTED` mới nhất). Nếu không suy ra được, dùng `REVIEWING`.
- Sau khi xác nhận: cập nhật `current_status`, ghi `ApplicationStatusHistory` (`from_status = REJECTED`, `to_status` = đích khôi phục, `changed_by = request.user`, ghi chú nêu đây là khôi phục).
- Endpoint khôi phục MUST NOT được Kanban gọi thay cho kéo thả.

**C. Nộp hồ sơ**
- Không đi qua bảng Kanban. Máy chủ tạo `APPLIED` và bản ghi lịch sử khởi tạo như mục nộp CV.

### Kanban
- Năm cột tương ứng năm trạng thái trên.
- Mỗi thẻ ứng viên hiển thị: họ tên, vị trí ứng tuyển, điểm phù hợp hoặc nhãn chưa chấm được, thời gian nộp.
- HR kéo thả bằng `SortableJS` trong phạm vi bảng chuyển thông thường.
- Cột `REJECTED`: không nhận kéo ra; khôi phục bằng thao tác riêng có xác nhận.
- Cập nhật trạng thái MUST qua view máy chủ; không tin sự kiện trình duyệt.
- View Kanban MUST kiểm tra cạnh hợp lệ loại A. View khôi phục MUST kiểm tra loại B.
- Sau khi đổi thành công:
  - cập nhật `Application.current_status`,
  - thêm đúng một bản ghi `ApplicationStatusHistory` với `changed_by = request.user`,
  - cập nhật thời gian sửa đổi.
- Nếu cần POST bất đồng bộ: ưu tiên Django view trả JSON. Chỉ dùng Django REST Framework khi cách đó không đủ.

### Lịch sử trạng thái
- HR xem được danh sách các lần thay đổi trạng thái theo thời gian giảm dần.
- Mỗi bản ghi hiển thị `from_status`, `to_status`, người thay đổi (`changed_by.full_name` và vai trò), thời gian và ghi chú ngắn nếu có.
- Bản ghi nộp hồ sơ hiển thị người thực hiện là Candidate.

### Ghi chú phỏng vấn
- HR thêm ghi chú cho từng hồ sơ.
- Ghi chú dùng để lưu nhận xét, kết quả từng vòng hoặc đề xuất tiếp theo.
- Ghi chú không thay thế lịch sử trạng thái; hai loại dữ liệu phải tách riêng.
- `created_by` là HR/Admin đang đăng nhập.

## 9. Đặc tả dashboard và số liệu thống kê

### Mục tiêu dashboard
Giúp HR nhìn nhanh tình hình tuyển dụng của hệ thống ở mức phù hợp với đồ án.

### Chỉ số bắt buộc
- Tổng số tin tuyển dụng.
- Số tin đang mở.
- Tổng số hồ sơ ứng tuyển.
- Số ứng viên theo từng trạng thái.
- Top tin tuyển dụng có nhiều hồ sơ nhất.

### Biểu đồ bắt buộc
- Biểu đồ cột hoặc tròn thể hiện phân bố hồ sơ theo trạng thái.
- Biểu đồ cột thể hiện số hồ sơ theo tin tuyển dụng.

### Chỉ số tùy chọn
- Điểm phù hợp trung bình theo từng tin tuyển dụng (chỉ tính hồ sơ `SCORED`, bỏ qua hồ sơ lỗi).
- Tỷ lệ đề nghị nhận việc:

```text
tỷ lệ OFFERED = (số hồ sơ current_status = OFFERED / tổng số hồ sơ) × 100%
```

  Ý nghĩa: phần trăm hồ sơ đang ở trạng thái đã đưa đề nghị nhận việc trên toàn bộ hồ sơ đã nộp. Chỉ số này **không** đếm hồ sơ từng vào phỏng vấn rồi bị `REJECTED`, và **không** dùng tên cũ `PASSED`. Khi tổng số hồ sơ = 0, hiển thị 0% hoặc “chưa có dữ liệu”, không chia cho 0.

### Yêu cầu hiển thị
- Dùng `Chart.js`.
- Dữ liệu dashboard có thể render server-side hoặc dùng DRF chỉ khi thật sự cần để cập nhật động.
- Chỉ HR và Admin được mở dashboard.

## 10. Cấu trúc Django project đề xuất

### Cấu trúc mức cao
- `config/`: cấu hình project Django, settings, urls. Chứa `AUTH_USER_MODEL = "accounts.User"` trước khi tạo migration đầu.
- `accounts/`: quản lý người dùng, đăng nhập, đăng ký, phân quyền.
- `jobs/`: quản lý tin tuyển dụng và hiển thị việc làm.
- `applications/`: quản lý hồ sơ ứng tuyển, upload CV, bảo vệ tải CV, trích xuất văn bản, chấm điểm, Kanban, lịch sử trạng thái, ghi chú phỏng vấn.
- `dashboard/`: tổng hợp số liệu và hiển thị thống kê.

### Trách nhiệm từng app

#### App `accounts`
- Custom user model kế thừa `AbstractUser`.
- Form đăng ký, đăng nhập dùng Django auth (không tự hash).
- View và template cho xác thực.
- Decorator hoặc mixin phân quyền theo `role`.
- Giao diện Admin đồ án: quản lý tài khoản và phân quyền đủ theo đặc tả.
- Đăng ký `User` trên Django Admin `/admin/` với cùng ràng buộc, chỉ phục vụ phát triển.

#### App `jobs`
- Model `JobPost` với `created_by`.
- CRUD tin tuyển dụng cho HR.
- Khi sửa nội dung JD, gọi service tính lại điểm của app `applications`.
- Danh sách việc làm cho Candidate đã đăng nhập.
- Chi tiết JD.

#### App `applications`
- Model `Application`, `ApplicationStatusHistory`, `InterviewNote`.
- Form nộp CV và kiểm tra tệp.
- View tải CV có kiểm tra quyền.
- Service trích xuất văn bản: PDF bằng `pdfminer.six`, DOCX bằng `python-docx`.
- Service/validate chuyển trạng thái Kanban và khôi phục `REJECTED`.
- Service tiền xử lý và chấm điểm: một vectorizer / một corpus theo từng `JobPost`.
- Service tính lại điểm và thứ hạng khi có CV mới hoặc JD đổi.
- Giao diện Kanban; ghi lịch sử với `changed_by` đúng user.

#### App `dashboard`
- Query tổng hợp thống kê.
- View và template dashboard; giới hạn HR/Admin.
- Chuẩn bị dữ liệu cho `Chart.js`.

### Dùng Django REST Framework khi nào
- Chỉ dùng nếu Kanban hoặc dashboard cần cập nhật dữ liệu bất đồng bộ thuận tiện hơn so với form POST thông thường hoặc view JSON thuần Django.
- Nếu giao diện xử lý tốt bằng Django template và POST chuẩn, có thể không dùng DRF ở phiên bản đầu.

## 11. Trường hợp lỗi cần xử lý

### Lỗi xác thực và phân quyền
- Sai tài khoản hoặc mật khẩu.
- Tài khoản bị khóa.
- Truy cập URL không đúng vai trò.
- Candidate xem hoặc tải hồ sơ/CV của người khác.
- Người chưa đăng nhập truy cập media CV.

### Lỗi dữ liệu tuyển dụng
- Thiếu trường bắt buộc khi tạo JD.
- Hạn nộp nhỏ hơn ngày hiện tại khi tạo tin `OPEN`.
- Thử nộp hồ sơ vào tin đã đóng, `DRAFT`, hoặc hết hạn.

### Lỗi tệp CV
- Sai phần mở rộng, hoặc nội dung không phải PDF/DOCX thật.
- MIME lệch loại so với nội dung (trừ `application/octet-stream` đã xác minh được).
- Tệp vượt 5 MB.
- Tệp bị hỏng hoặc không đọc được.
- CV trống hoặc trích xuất ra dưới 100 ký tự sau chuẩn hóa.

### Lỗi ứng tuyển
- Candidate nộp trùng vào cùng một tin.
- Email trùng sau chuẩn hóa khi đăng ký hoặc tạo user.
- Không tìm thấy bản ghi ứng tuyển.
- Cập nhật trạng thái cho hồ sơ không tồn tại.
- Kéo Kanban sang trạng thái không hợp lệ (kể cả `REJECTED` → `INTERVIEW`).
- Gọi khôi phục khi hồ sơ không phải `REJECTED` hoặc khi chưa xác nhận.
- Đổi trạng thái mà không ghi được lịch sử (phải rollback).

### Lỗi chấm điểm
- Không tạo được vector TF-IDF vì không có CV hợp lệ hoặc JD rỗng sau chuẩn hóa.
- Không tính được điểm do lỗi thư viện hoặc dữ liệu đầu vào.
- Không xếp hạng hồ sơ thiếu điểm hợp lệ; không lấy 0 thay thế.

### Lỗi dashboard
- Không có dữ liệu để hiển thị biểu đồ.
- Dữ liệu thống kê không đồng nhất do trạng thái thiếu chuẩn hóa.

## 12. Các trường hợp kiểm thử quan trọng

### Kiểm thử chức năng
- Đăng ký Candidate thành công; thông báo rồi chuyển trang đăng nhập; không tự login; mật khẩu được Django hash, không lưu plaintext.
- Email bắt buộc, unique sau chuẩn hóa; `A@Mail.com` và `a@mail.com` bị coi là trùng.
- Đăng nhập đúng vai trò và điều hướng đúng.
- Admin tạo tài khoản HR.
- HR tạo, sửa, đóng tin tuyển dụng.
- Candidate xem danh sách việc làm và nộp CV hợp lệ.
- Candidate không nộp trùng cùng một tin.
- Nộp hồ sơ tạo lịch sử `APPLIED` với `changed_by` là Candidate.
- HR đổi trạng thái: lịch sử ghi đúng tài khoản HR/Admin.
- CV PDF và DOCX được trích xuất nội dung thành công.
- Hai hay nhiều CV cùng một tin được chấm trên cùng corpus; điểm dùng để xếp hạng thống nhất.
- Sửa JD làm tính lại điểm và thứ hạng của tin đó.
- Hồ sơ không đọc được hoặc văn bản rỗng không nhận `similarity_score = 0`.
- Hệ thống xếp hạng chỉ trên hồ sơ `SCORED`.
- HR kéo thả Kanban theo cạnh hợp lệ; máy chủ từ chối `REJECTED` → `INTERVIEW`.
- Khôi phục hồ sơ từ chối nhầm chỉ qua thao tác riêng có xác nhận và có bản ghi lịch sử.
- HR thêm ghi chú phỏng vấn.
- Candidate chỉ xem được hồ sơ của mình khi gọi trực tiếp URL.
- Dashboard hiển thị đúng các chỉ số cơ bản.

### Kiểm thử bảo mật và phân quyền
- Candidate không truy cập được màn hình HR/Admin.
- HR không truy cập được chức năng quản trị tài khoản nếu không được cấp quyền Admin.
- Người chưa đăng nhập không nộp CV được.
- Người chưa đăng nhập hoặc sai quyền không tải được tệp CV.
- Form đăng ký công khai không tạo được tài khoản `ADMIN` hoặc `HR`.

### Kiểm thử dữ liệu và biên
- JD rỗng hoặc CV rỗng bị từ chối xử lý phù hợp, không coi là điểm 0.
- File sai định dạng, nội dung giả mạo phần mở rộng, hoặc quá 5 MB bị chặn.
- File hợp lệ với `content_type = application/octet-stream` được chấp nhận.
- Tin tuyển dụng hết hạn không nhận hồ sơ mới.
- Điểm similarity khi `SCORED` luôn nằm trong khoảng hợp lệ.
- `AUTH_USER_MODEL` trỏ `accounts.User` và migration đầu tạo đúng bảng user tùy chỉnh.
- Không dùng `PyPDF2`. PDF lỗi để `EXTRACTION_FAILED`, không gán điểm 0.

## 13. Giả định triển khai
- Hệ thống phục vụ quy mô nhỏ, phù hợp demo đồ án và kiểm thử trên máy cá nhân.
- Không yêu cầu xử lý đồng thời lớn. Việc fit lại TF-IDF theo từng tin khi có CV mới là chấp nhận được ở quy mô đồ án.
- Candidate tự đăng ký; HR và Admin do Admin tạo hoặc seed dữ liệu ban đầu.
- Chưa có database cũ: custom user được khai báo trước migration đầu, không cần quy trình migrate từ `auth.User`.

## 14. Quyết định đã chốt

Không còn mục kỹ thuật mở trước Task 1.

- Email bắt buộc, unique, chuẩn hóa rồi mới kiểm tra trùng; `EmailField(254)`; kiểm tra máy chủ và unique trên CSDL; không ngoại lệ demo. Độ dài email **không** cắt xuống 100 ký tự.
- CV tối đa 5 MB; chỉ PDF và DOCX; kiểm tra phần mở rộng, **nội dung thực tế**, dung lượng; `application/octet-stream` được chấp nhận nếu đã xác minh PDF/DOCX thật; lỗi/rỗng/không trích xuất được thì có `scoring_status`, không gán điểm 0.
- Kanban: `APPLIED` ↔ `REVIEWING` ↔ `INTERVIEW` → `OFFERED`; từ các trạng thái trên (trừ đích không nằm bảng) có thể sang `REJECTED`; `OFFERED` chỉ sang `REJECTED`; không kéo `REJECTED` đi nơi khác bằng thao tác thường.
- Khôi phục `REJECTED`: thao tác riêng, có xác nhận, về trạng thái ngay trước lần từ chối; thiếu lịch sử thì về `REVIEWING`; ghi `ApplicationStatusHistory`.
- Ngưỡng văn bản tối thiểu để chấm điểm: **100 ký tự** sau chuẩn hóa (CV/JD), không phải giới hạn email.
- Chỉ số tùy chọn dashboard: `(số OFFERED / tổng số hồ sơ) × 100%`, nghĩa là tỷ lệ hồ sơ đang được đề nghị nhận việc.
- PDF chỉ `pdfminer.six`; DOCX chỉ `python-docx`; không `PyPDF2` ở phiên bản đầu.
- Sau đăng ký: thông báo và chuyển trang đăng nhập; không tự login.
- Giữ `/admin/` và Admin đồ án; cả hai tuân thủ cùng quy tắc email đã chuẩn hóa/unique và `role` bắt buộc. `/admin/` không bắt buộc trong buổi demo.

## MODIFIED Requirements
### Requirement: Dùng Django REST Framework ở mức tối thiểu
Hệ thống chỉ sử dụng Django REST Framework khi thật sự cần cho các tương tác bất đồng bộ như Kanban hoặc dashboard; còn lại ưu tiên Django view và template truyền thống để giảm độ phức tạp.

### Requirement: Custom user model trước migration đầu
Hệ thống SHALL khai báo `AUTH_USER_MODEL = "accounts.User"` với `User` kế thừa `AbstractUser` trước lần migrate đầu tiên, và dùng Django Authentication cho toàn bộ đăng nhập, mật khẩu, session.

### Requirement: Chấm điểm CV-JD nhất quán theo từng tin tuyển dụng
Hệ thống SHALL fit một `TfidfVectorizer` trên corpus gồm JD và các CV hợp lệ của cùng `JobPost`, tính Cosine Similarity trên cùng bộ biểu diễn đó, rồi mới xếp hạng. Hệ thống SHALL tính lại khi có CV mới hoặc JD đổi. Hệ thống SHALL NOT gán điểm 0 cho hồ sơ trích xuất thất bại hoặc văn bản rỗng.

### Requirement: Email bắt buộc, duy nhất, đã chuẩn hóa
Hệ thống SHALL bắt buộc email, chuẩn hóa (cắt khoảng trắng, chữ thường) trước khi kiểm tra trùng, có unique trên CSDL, kiểm tra phía máy chủ, và không tạo ngoại lệ cho tài khoản demo.

### Requirement: Luồng trạng thái tuyển dụng có kiểm soát
Hệ thống SHALL dùng đúng năm trạng thái `APPLIED`, `REVIEWING`, `INTERVIEW`, `OFFERED`, `REJECTED`, chỉ nhận chuyển hợp lệ phía máy chủ, ghi mọi thay đổi vào `ApplicationStatusHistory`, và chỉ khôi phục `REJECTED` qua thao tác riêng có xác nhận.

## REMOVED Requirements
### Requirement: Mở rộng thành hệ thống tuyển dụng doanh nghiệp nhiều tầng
**Reason**: Không phù hợp phạm vi đồ án tốt nghiệp đại học và làm tăng chi phí triển khai, kiểm thử.
**Migration**: Chỉ giữ quy trình tuyển dụng cơ bản một cấp với các trạng thái tối thiểu, tập trung vào luồng CV-JD, Kanban và dashboard.
