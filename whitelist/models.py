from django.db import models
from django.conf import settings

class WhitelistApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    # User Information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    your_name = models.CharField(max_length=100, help_text="Your real name", null=True, blank=True)
    your_age = models.PositiveIntegerField(help_text="Your real age", null=True, blank=True)
    your_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, help_text="Your gender", null=True, blank=True)
    discord_name = models.CharField(max_length=100, help_text="Your Discord username", null=True, blank=True)
    
    # Character Information
    character_name = models.CharField(max_length=100, help_text="Your character's name")
    character_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, help_text="Your character's gender")
    character_age = models.PositiveIntegerField(help_text="Your character's age")
    
    # Acknowledgment
    rules_acknowledged = models.BooleanField(default=False, help_text="I have read and understood the server rules")
    
    # Application Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Application by {self.your_name or self.user} - {self.status}"