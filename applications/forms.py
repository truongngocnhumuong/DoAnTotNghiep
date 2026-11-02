"""
applications/forms.py

Form nộp hồ sơ ứng tuyển với kiểm tra đầy đủ:
  - Phần mở rộng: chỉ .pdf hoặc .docx
  - Magic bytes / cấu trúc tệp thực tế
  - Dung lượng tối đa 5 MB
  - Chấp nhận content_type = application/octet-stream khi nội dung đã xác minh
"""

import zipfile

from django import forms

# ─────────────────────────────────────────────
# Hằng số
# ─────────────────────────────────────────────
MAX_SIZE_BYTES = 5 * 1024 * 1024          # 5 MB
ALLOWED_EXTENSIONS = {"pdf", "docx"}

PDF_MAGIC = b"%PDF"                        # 4 byte đầu của tệp PDF
DOCX_REQUIRED_ENTRY = "[Content_Types].xml"  # Entry bắt buộc trong zip của DOCX

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",            # trình duyệt đôi khi gửi kiểu này
}


# ─────────────────────────────────────────────
# Validator nội bộ — được gọi từ clean_cv_file
# ─────────────────────────────────────────────

def _get_extension(filename: str) -> str:
    """Trả về phần mở rộng lowercase không có dấu chấm."""
    parts = filename.rsplit(".", 1)
    return parts[-1].lower() if len(parts) == 2 else ""


def _validate_pdf_magic(file_obj) -> bool:
    """Kiểm tra 4 byte đầu có đúng magic PDF không."""
    file_obj.seek(0)
    header = file_obj.read(4)
    file_obj.seek(0)
    return header == PDF_MAGIC


def _validate_docx_structure(file_obj) -> bool:
    """
    Kiểm tra tệp có cấu trúc DOCX hợp lệ không:
      - Là ZIP hợp lệ
      - Có chứa [Content_Types].xml
      - Có chứa thư mục word/
    """
    file_obj.seek(0)
    try:
        with zipfile.ZipFile(file_obj, "r") as zf:
            names = zf.namelist()
            has_content_types = DOCX_REQUIRED_ENTRY in names
            has_word_dir = any(n.startswith("word/") for n in names)
            return has_content_types and has_word_dir
    except (zipfile.BadZipFile, Exception):
        return False
    finally:
        file_obj.seek(0)


# ─────────────────────────────────────────────
# Form chính
# ─────────────────────────────────────────────

class ApplicationForm(forms.Form):
    """
    Form nộp hồ sơ ứng tuyển cho Candidate.

    Chỉ có 1 trường: cv_file — tệp CV (PDF hoặc DOCX, tối đa 5 MB).
    Validate theo thứ tự:
      1. Có tệp không
      2. Dung lượng <= 5 MB
      3. Phần mở rộng hợp lệ (.pdf / .docx)
      4. Content-type hợp lệ (cho phép octet-stream)
      5. Magic bytes / cấu trúc thực tế khớp với phần mở rộng
    """

    cv_file = forms.FileField(
        label="Tệp CV (PDF hoặc DOCX, tối đa 5 MB)",
        help_text="Chấp nhận định dạng .pdf hoặc .docx, dung lượng không quá 5 MB.",
        widget=forms.ClearableFileInput(attrs={
            "accept": ".pdf,.docx",
            "class": "form-control",
        }),
    )

    def clean_cv_file(self):
        file = self.cleaned_data.get("cv_file")
        if not file:
            raise forms.ValidationError("Vui lòng chọn tệp CV để nộp.")

        # ── 1. Dung lượng ──────────────────────────────────────────────
        if file.size > MAX_SIZE_BYTES:
            raise forms.ValidationError(
                f"Tệp quá lớn ({file.size / 1024 / 1024:.1f} MB). "
                f"Dung lượng tối đa cho phép là 5 MB."
            )

        # ── 2. Phần mở rộng ────────────────────────────────────────────
        ext = _get_extension(file.name)
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'Định dạng tệp ".{ext}" không được hỗ trợ. '
                "Chỉ chấp nhận tệp .pdf hoặc .docx."
            )

        # ── 3. Content-type ────────────────────────────────────────────
        content_type = getattr(file, "content_type", "") or ""
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError(
                f'Kiểu tệp "{content_type}" không được hỗ trợ. '
                "Vui lòng tải lên tệp PDF hoặc DOCX hợp lệ."
            )

        # ── 4. Magic bytes / cấu trúc thực tế ─────────────────────────
        if ext == "pdf":
            if not _validate_pdf_magic(file):
                raise forms.ValidationError(
                    "Tệp không phải là PDF hợp lệ (nội dung không đúng định dạng)."
                )
        elif ext == "docx":
            if not _validate_docx_structure(file):
                raise forms.ValidationError(
                    "Tệp không phải là DOCX hợp lệ "
                    "(cấu trúc ZIP / Word không đúng định dạng)."
                )

        return file
