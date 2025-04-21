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
    
    # Discord Information
    discord_name = models.CharField(max_length=100, help_text="Discord Name & Tag (e.g., JohnDoe#1234)")
    
    # Steam Information
    steam_name = models.CharField(max_length=100, help_text="Steam Name")
    steam_hex_id = models.CharField(max_length=100, help_text="Steam Hex ID")
    
    # Personal Information
    age = models.PositiveIntegerField(help_text="Your age")
    
    # Server Information
    fivem_experience = models.TextField(help_text="How long have you been playing on FiveM?")
    
    # Character Information
    character_name = models.CharField(max_length=100, help_text="Character Name (First & Last)")
    character_age = models.PositiveIntegerField(help_text="Character Age")
    
    # Roleplay Knowledge
    rule_breaking_response = models.TextField(help_text="What would you do if you saw someone breaking the rules?")
    
    # Acknowledgment
    rules_acknowledged = models.BooleanField(default=False, help_text="Do you agree to follow all rules and respect staff decisions?")
    
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
        return f"Application by {self.discord_name} - {self.status}"