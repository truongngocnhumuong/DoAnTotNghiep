from django import forms
from django.utils import timezone

from .models import JobPost


class JobPostForm(forms.ModelForm):
    """Form tạo và chỉnh sửa tin tuyển dụng dành cho HR / Admin."""

    class Meta:
        model = JobPost
        fields = (
            "title",
            "department",
            "location",
            "employment_type",
            "description",
            "requirements",
            "benefits",
            "deadline",
            "status",
        )
        labels = {
            "title": "Tiêu đề vị trí",
            "department": "Phòng / Ban",
            "location": "Địa điểm",
            "employment_type": "Hình thức làm việc",
            "description": "Mô tả công việc",
            "requirements": "Yêu cầu ứng viên",
            "benefits": "Quyền lợi",
            "deadline": "Hạn nộp hồ sơ",
            "status": "Trạng thái tin",
        }
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 6}),
            "requirements": forms.Textarea(attrs={"rows": 6}),
            "benefits": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "status": (
                "Nháp: chưa hiển thị với ứng viên. "
                "Đang mở: ứng viên có thể nộp hồ sơ. "
                "Đã đóng: ngừng nhận hồ sơ."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")
        # Deadline: đặt input_formats để parse đúng
        self.fields["deadline"].input_formats = ["%Y-%m-%d"]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        deadline = cleaned_data.get("deadline")
        if status == JobPost.Status.OPEN and deadline and deadline < timezone.localdate():
            self.add_error(
                "deadline",
                "Hạn nộp không được nhỏ hơn ngày hiện tại khi tin đang mở tuyển.",
            )
        return cleaned_data
