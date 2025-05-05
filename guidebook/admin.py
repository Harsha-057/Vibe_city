from django.contrib import admin
from .models import GuidebookEntry

class GuidebookEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'order', 'created_at', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')
    ordering = ('order', 'created_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description')
        }),
        ('Media', {
            'fields': ('thumbnail', 'video_url')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )

admin.site.register(GuidebookEntry, GuidebookEntryAdmin)
