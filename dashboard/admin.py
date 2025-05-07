from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LogEntry

# Set the admin site header and title
admin.site.site_header = _('Vibe City RP Administration')
admin.site.site_title = _('Vibe City RP Admin')
admin.site.index_title = _('Welcome to Vibe City RP Administration')

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('timestamp', 'user', 'action')
    search_fields = ('action', 'description', 'user__username')
    readonly_fields = ('timestamp',)



