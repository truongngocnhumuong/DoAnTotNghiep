from django.contrib import admin

from .models import JobPost


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "status", "deadline", "created_by", "created_at")
    list_filter = ("status", "department", "employment_type")
    search_fields = ("title", "department", "location", "created_by__username")
    autocomplete_fields = ("created_by",)
