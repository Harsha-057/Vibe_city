from django.contrib import admin
from .models import JobApplication

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_type', 'status', 'submitted_at', 'reviewed_at', 'reviewer')
    list_filter = ('job_type', 'status', 'submitted_at', 'reviewed_at')
    search_fields = ('applicant__username', 'applicant__discord_username', 'character_name', 'reason', 'feedback')
    readonly_fields = ('submitted_at', 'reviewed_at', 'reviewer')
    list_per_page = 25

    fieldsets = (
        ('Application Info', {
            'fields': ('applicant', 'job_type', 'character_name', 'date_of_birth', 'status', 'submitted_at')
        }),
        ('Application Content', {
            'fields': ('previous_experience', 'reason')
        }),
        ('Job Specific Answers', {
            'classes': ('collapse',), # Collapsible section
            'fields': (
                'sasp_scenario_response', 'sasp_leadership_experience',
                'ems_medical_certification', 'ems_pressure_handling',
                'mechanic_skills', 'mechanic_tool_knowledge'
            )
        }),
        ('Review', {
             'fields': ('reviewer', 'reviewed_at', 'feedback')
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
