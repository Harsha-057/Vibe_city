from django.db import models
from django.utils.translation import gettext_lazy as _

class Keybind(models.Model):
    name = models.CharField(_('Name'), max_length=100, help_text=_('Name of the keybind action'))
    description = models.TextField(_('Description'), help_text=_('Description of what this keybind does'))
    key = models.CharField(_('Key'), max_length=50, help_text=_('The key to bind (e.g., F1, E, etc.)'))
    command = models.CharField(_('Command'), max_length=255, help_text=_('The command to execute when key is pressed'))
    category = models.CharField(_('Category'), max_length=50, help_text=_('Category of the keybind (e.g., General, Vehicle, etc.)'))
    is_active = models.BooleanField(_('Active'), default=True, help_text=_('Whether this keybind is currently active'))
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Keybind')
        verbose_name_plural = _('Keybinds')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.key})"
