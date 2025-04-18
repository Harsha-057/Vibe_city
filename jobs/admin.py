from django.contrib import admin
from .models import JobApplication
from django.utils import timezone # Import timezone if needed for actions

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
                'sasp_scenario_response', 'sasp_leadership_experience',
                'ems_medical_certification', 'ems_pressure_handling',
                'mechanic_skills', 'mechanic_tool_knowledge'
            )
        }),
        ('Form Review', {
             'fields': ('form_reviewer', 'form_reviewed_at', 'form_feedback')
        }),
        ('Interview/Final Decision', {
             'fields': ('interview_reviewer', 'interview_reviewed_at', 'interview_feedback')
        }),
    )

    # Optional: Add actions like bulk approve/reject later
    # actions = ['approve_applications', 'reject_applications']

    # def approve_applications(self, request, queryset):
    #     queryset.update(status='APPROVED', reviewer=request.user, reviewed_at=timezone.now())
    #     self.message_user(request, f'{queryset.count()} applications approved.')
    # approve_applications.short_description = "Mark selected applications as Approved"

    # def reject_applications(self, request, queryset):
    #     queryset.update(status='REJECTED', reviewer=request.user, reviewed_at=timezone.now())
    #     self.message_user(request, f'{queryset.count()} applications rejected.')
    # reject_applications.short_description = "Mark selected applications as Rejected"
