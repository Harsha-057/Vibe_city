from django.db import models
from django.utils import timezone

class GalleryImage(models.Model):
    CATEGORY_CHOICES = (
        ('locations', 'Locations'),
        ('vehicles', 'Vehicles'),
        ('events', 'Events'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(help_text="URL of the image")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return self.title 