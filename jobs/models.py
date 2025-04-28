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
        ('PENDING', 'Pending Form Review'),
        ('INTERVIEW_PENDING', 'Pending Interview'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected (Form Stage)'),
        ('REJECTED_INTERVIEW', 'Rejected (Interview Stage)'),
        ('FIRED', 'Fired'),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=10, choices=JOB_CHOICES)
    character_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(help_text="In-game character date of birth")
    previous_experience = models.TextField(blank=True, help_text="Describe any relevant previous experience.")
    reason = models.TextField(help_text="Why are you applying for this position?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    form_reviewed_at = models.DateTimeField(null=True, blank=True)
    form_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_job_forms'
    )
    form_feedback = models.TextField(null=True, blank=True, help_text="Feedback provided during form review.")

    interview_reviewed_at = models.DateTimeField(null=True, blank=True)
    interview_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interviewed_job_applicants'
    )
    interview_feedback = models.TextField(null=True, blank=True, help_text="Feedback provided during/after interview.")

    # --- Job Specific Fields --- #
    # SASP
    sasp_scenario_response = models.TextField(null=True, blank=True, help_text="Describe how you would handle a specific scenario (e.g., a high-speed pursuit ending in a crash).")
    sasp_leadership_experience = models.TextField(null=True, blank=True, help_text="Describe any relevant leadership experience (Optional).")

    # SASP specific fields
    irl_name = models.CharField(max_length=255, null=True, blank=True)
    irl_age = models.IntegerField(null=True, blank=True)
    discord_name = models.CharField(max_length=255, null=True, blank=True)
    character_backstory = models.TextField(null=True, blank=True)
    past_experience = models.TextField(null=True, blank=True)
    
    # PD Rules Fields
    pd_rules_vehicle_pursuit = models.TextField(null=True, blank=True)
    pd_rules_use_of_force = models.TextField(null=True, blank=True)
    pd_rules_traffic_stops = models.TextField(null=True, blank=True)
    pd_rules_evidence = models.TextField(null=True, blank=True)
    pd_rules_miranda = models.TextField(null=True, blank=True)
    pd_rules_radio = models.TextField(null=True, blank=True)
    pd_rules_officer_down = models.TextField(null=True, blank=True)
    pd_rules_scene_management = models.TextField(null=True, blank=True)

    # EMS
    ems_interest = models.TextField(null=True, blank=True)
    ems_qualities = models.TextField(null=True, blank=True)
    ems_helped_someone = models.TextField(null=True, blank=True)
    ems_pressure_handling = models.TextField(null=True, blank=True)

    # Mechanic
    mechanic_skills = models.TextField(null=True, blank=True)
    mechanic_tool_knowledge = models.TextField(null=True, blank=True)
    mechanic_problem_solving = models.TextField(null=True, blank=True)
    mechanic_interest = models.TextField(null=True, blank=True)

    # EMS specific fields
    ems_medical_certification = models.CharField(max_length=255, null=True, blank=True)
    ems_pressure_handling = models.TextField(null=True, blank=True)

    # Mechanic specific fields
    mechanic_skills = models.TextField(null=True, blank=True)
    mechanic_tool_knowledge = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.applicant.username} - {self.get_job_type_display()} ({self.get_status_display()})"
