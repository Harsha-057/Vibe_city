from django.db import models
from django.conf import settings

# Create your models here.

class JobApplication(models.Model):
    JOB_CHOICES = [
        ('SASP', 'San Andreas State Police'),
        ('EMS', 'Emergency Medical Services'),
        ('MECHANIC', 'Mechanic'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=10, choices=JOB_CHOICES)
    character_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(help_text="In-game character date of birth")
    previous_experience = models.TextField(blank=True, help_text="Describe any relevant previous experience.")
    reason = models.TextField(help_text="Why are you applying for this position?")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_job_applications'
    )

    # --- Job Specific Fields --- #
    # SASP
    sasp_scenario_response = models.TextField(null=True, blank=True, help_text="Describe how you would handle a specific scenario (e.g., a high-speed pursuit ending in a crash).")
    sasp_leadership_experience = models.TextField(null=True, blank=True, help_text="Describe any relevant leadership experience (Optional).")

    # EMS
    ems_medical_certification = models.CharField(max_length=255, null=True, blank=True, help_text="Do you hold any relevant medical certifications? (e.g., EMT, Paramedic) (Optional)")
    ems_pressure_handling = models.TextField(null=True, blank=True, help_text="Describe how you handle high-pressure situations.")

    # Mechanic
    mechanic_skills = models.TextField(null=True, blank=True, help_text="List your relevant mechanical skills and experience (e.g., engine repair, tuning, bodywork).")
    mechanic_tool_knowledge = models.BooleanField(null=True, blank=True, help_text="Do you own or have extensive knowledge of specialized mechanic tools? (Optional)")

    # --- Reviewer Feedback --- #
    feedback = models.TextField(null=True, blank=True, help_text="Feedback provided by the reviewer.")

    def __str__(self):
        return f"{self.applicant.username} - {self.get_job_type_display()} Application"
