from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "full_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("username",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Thông tin bổ sung", {"fields": ("full_name", "role", "phone")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Thông tin bổ sung", {"fields": ("email", "full_name", "role", "phone")}),
    )
