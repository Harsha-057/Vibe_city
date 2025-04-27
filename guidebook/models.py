from django.db import models
from django.utils import timezone

class GuidebookEntry(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='guidebook/thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "Guidebook Entries"

    def __str__(self):
        return self.title
