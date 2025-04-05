from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard_log_entries', null=True, blank=True)
    action = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
