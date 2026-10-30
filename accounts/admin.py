from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.forms import DjangoAdminUserChangeForm, DjangoAdminUserCreationForm
from accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = DjangoAdminUserChangeForm
    add_form = DjangoAdminUserCreationForm
    list_display = ("username", "email", "full_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân", {"fields": ("full_name", "email", "phone")}),
        ("Vai trò và trạng thái", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Quyền", {"fields": ("groups", "user_permissions")}),
        ("Thời gian", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "full_name",
                    "role",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
