from django.contrib import admin
from .models import JobApplication
from django.utils import timezone

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_type', 'status', 'submitted_at', 'form_reviewed_at', 'form_reviewer', 'interview_reviewed_at', 'interview_reviewer')
    list_filter = ('job_type', 'status', 'submitted_at', 'form_reviewed_at', 'interview_reviewed_at')
    search_fields = ('applicant__username', 'applicant__discord_username', 'character_name', 'reason', 'form_feedback', 'interview_feedback')
    readonly_fields = ('submitted_at', 'form_reviewed_at', 'form_reviewer', 'interview_reviewed_at', 'interview_reviewer')
    list_per_page = 25

    fieldsets = (
        ('Application Info', {
            'fields': ('applicant', 'job_type', 'character_name', 'date_of_birth', 'status', 'submitted_at')
        }),
        ('Application Content', {
            'fields': ('previous_experience', 'reason')
        }),
        ('Job Specific Answers', {
            'classes': ('collapse',),
            'fields': (
                'irl_name', 'irl_age', 'discord_name',
                'character_backstory', 'past_experience', 'pd_rules_vehicle_pursuit', 'pd_rules_use_of_force',
                'pd_rules_traffic_stops', 'pd_rules_evidence', 'pd_rules_miranda', 'pd_rules_radio',
                'pd_rules_officer_down', 'pd_rules_scene_management',
                'ems_interest', 'ems_qualities', 'ems_helped_someone', 'ems_pressure_handling',
                'mechanic_skills', 'mechanic_tool_knowledge', 'mechanic_problem_solving', 'mechanic_interest'
            )
        }),
        ('Form Review', {
             'fields': ('form_reviewer', 'form_reviewed_at', 'form_feedback')
        }),
        ('Interview/Final Decision', {
             'fields': ('interview_reviewer', 'interview_reviewed_at', 'interview_feedback')
        }),
    )

    actions = ['approve_form_review', 'reject_form_review', 'schedule_interview', 'hire_applicant', 'reject_interview', 'fire_applicant']

    def approve_form_review(self, request, queryset):
        queryset.update(
            status='INTERVIEW_PENDING',
            form_reviewer=request.user,
            form_reviewed_at=timezone.now()
        )
        self.message_user(request, f'{queryset.count()} applications moved to interview stage.')
    approve_form_review.short_description = "Approve form review and move to interview"

    def reject_form_review(self, request, queryset):
        queryset.update(
            status='REJECTED',
            form_reviewer=request.user,
            form_reviewed_at=timezone.now()
        )
        self.message_user(request, f'{queryset.count()} applications rejected at form stage.')
    reject_form_review.short_description = "Reject at form review stage"

    def schedule_interview(self, request, queryset):
        queryset.update(status='INTERVIEW_PENDING')
        self.message_user(request, f'{queryset.count()} applications scheduled for interview.')
    schedule_interview.short_description = "Schedule for interview"

    def hire_applicant(self, request, queryset):
        queryset.update(
            status='HIRED',
            interview_reviewer=request.user,
            interview_reviewed_at=timezone.now()
        )
        self.message_user(request, f'{queryset.count()} applicants hired.')
    hire_applicant.short_description = "Hire selected applicants"

    def reject_interview(self, request, queryset):
        queryset.update(
            status='REJECTED_INTERVIEW',
            interview_reviewer=request.user,
            interview_reviewed_at=timezone.now()
        )
        self.message_user(request, f'{queryset.count()} applications rejected at interview stage.')
    reject_interview.short_description = "Reject at interview stage"

    def fire_applicant(self, request, queryset):
        queryset.update(status='FIRED')
        self.message_user(request, f'{queryset.count()} employees fired.')
    fire_applicant.short_description = "Fire selected employees"
