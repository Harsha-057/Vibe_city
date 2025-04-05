from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LogEntry

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    if sender != LogEntry:  # Avoid logging LogEntry saves
        action = 'Created' if created else 'Updated'
        LogEntry.objects.create(
            user=instance.user if hasattr(instance, 'user') else None,
            action=action,
            description=f'{sender.__name__} instance {action.lower()} with ID {instance.pk}'
        ) 