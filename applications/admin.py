from django.contrib import admin

from .models import Application, ApplicationStatusHistory, InterviewNote


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "job_post",
        "current_status",
        "scoring_status",
        "similarity_score",
        "ranking_position",
        "applied_at",
    )
    list_filter = ("current_status", "scoring_status", "job_post")
    search_fields = ("candidate__username", "candidate__full_name", "job_post__title")
    autocomplete_fields = ("job_post", "candidate")


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("application", "from_status", "to_status", "changed_by", "changed_at")
    list_filter = ("to_status",)
    search_fields = ("application__job_post__title", "application__candidate__full_name")
    autocomplete_fields = ("application", "changed_by")


@admin.register(InterviewNote)
class InterviewNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "application", "created_by", "interview_round", "created_at")
    search_fields = ("title", "application__job_post__title", "application__candidate__full_name")
    autocomplete_fields = ("application", "created_by")
