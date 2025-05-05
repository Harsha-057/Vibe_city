from django.db import models

class Questions(models.Model):
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Question {self.id}" 