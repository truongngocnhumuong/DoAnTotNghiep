from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password

from accounts.models import User, normalize_user_email
from accounts.utils import validate_unique_normalized_email


def bootstrap_widget(widget):
    widget.attrs.setdefault("class", "form-control")
    return widget


class CandidateRegistrationForm(forms.Form):
    username = forms.CharField(
        label="Tên đăng nhập",
        max_length=150,
        validators=User._meta.get_field("username").validators,
    )
    email = forms.EmailField(label="Email", max_length=254)
    full_name = forms.CharField(label="Họ và tên", max_length=150)
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Xác nhận mật khẩu", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            bootstrap_widget(field.widget)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập này đã được sử dụng.")
        return username

    def clean_email(self):
        return validate_unique_normalized_email(self.cleaned_data.get("email"))

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if not full_name:
            raise forms.ValidationError("Họ tên là bắt buộc.")
        return full_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Mật khẩu xác nhận không khớp.")
        if password:
            user = User(
                username=cleaned_data.get("username") or "",
                email=cleaned_data.get("email") or "",
                full_name=cleaned_data.get("full_name") or "",
            )
            try:
                validate_password(password, user=user)
            except forms.ValidationError as exc:
                self.add_error("password", exc)
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            full_name=self.cleaned_data["full_name"],
            role=User.Role.CANDIDATE,
            is_active=True,
        )


class RoleBasedAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Tên đăng nhập hoặc mật khẩu không đúng.",
        "inactive": "Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Tên đăng nhập"
        self.fields["password"].label = "Mật khẩu"
        for field in self.fields.values():
            bootstrap_widget(field.widget)


class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Xác nhận mật khẩu", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "role", "phone", "is_active", "is_staff")
        labels = {
            "username": "Tên đăng nhập",
            "email": "Email",
            "full_name": "Họ và tên",
            "role": "Vai trò",
            "phone": "Số điện thoại",
            "is_active": "Tài khoản hoạt động",
            "is_staff": "Cho phép vào Django Admin",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].required = True
        self.fields["email"].required = True
        self.fields["full_name"].required = True
        for name, field in self.fields.items():
            if name in {"is_active", "is_staff"}:
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                bootstrap_widget(field.widget)

    def clean_email(self):
        return validate_unique_normalized_email(self.cleaned_data.get("email"), instance=self.instance)

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role not in User.Role.values:
            raise forms.ValidationError("Vai trò không hợp lệ.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Mật khẩu xác nhận không khớp.")
        if password:
            try:
                validate_password(password, user=self.instance)
            except forms.ValidationError as exc:
                self.add_error("password", exc)
        return cleaned_data

    def save(self, commit=True):
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            full_name=self.cleaned_data["full_name"],
            role=self.cleaned_data["role"],
            phone=self.cleaned_data.get("phone") or None,
            is_active=self.cleaned_data.get("is_active", True),
            is_staff=self.cleaned_data.get("is_staff", False),
        )


class AdminUserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput,
        required=False,
        help_text="Để trống nếu không đổi mật khẩu.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "role", "phone", "is_active", "is_staff")
        labels = {
            "username": "Tên đăng nhập",
            "email": "Email",
            "full_name": "Họ và tên",
            "role": "Vai trò",
            "phone": "Số điện thoại",
            "is_active": "Tài khoản hoạt động",
            "is_staff": "Cho phép vào Django Admin",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].required = True
        self.fields["email"].required = True
        self.fields["full_name"].required = True
        for name, field in self.fields.items():
            if name in {"is_active", "is_staff"}:
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                bootstrap_widget(field.widget)

    def clean_email(self):
        return validate_unique_normalized_email(self.cleaned_data.get("email"), instance=self.instance)

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role not in User.Role.values:
            raise forms.ValidationError("Vai trò không hợp lệ.")
        return role

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password, user=self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = normalize_user_email(user.email)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class DjangoAdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "full_name", "role", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["full_name"].required = True
        self.fields["role"].required = True

    def clean_email(self):
        return validate_unique_normalized_email(self.cleaned_data.get("email"), instance=self.instance)

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if not role:
            raise forms.ValidationError("Vai trò là bắt buộc.")
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = normalize_user_email(user.email)
        if not user.role:
            raise forms.ValidationError({"role": "Vai trò là bắt buộc."})
        if commit:
            user.save()
        return user


class DjangoAdminUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_email(self):
        return validate_unique_normalized_email(self.cleaned_data.get("email"), instance=self.instance)

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if not role:
            raise forms.ValidationError("Vai trò là bắt buộc.")
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = normalize_user_email(user.email)
        if commit:
            user.save()
            self.save_m2m()
        return user
