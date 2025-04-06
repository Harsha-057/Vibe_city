from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
import sys

@receiver(post_save)
def log_model_save(sender, instance, **kwargs):
    # Don't run during migration commands
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
        return

    LogEntry = apps.get_model('dashboard', 'LogEntry')
    action = 'Created' if kwargs.get('created', False) else 'Updated'

