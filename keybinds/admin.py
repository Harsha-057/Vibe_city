from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Keybind

@admin.register(Keybind)
class KeybindAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'category', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'key', 'command')
    list_editable = ('is_active',)
    ordering = ('category', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Keybind Configuration', {
            'fields': ('key', 'command')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('key',)
        return self.readonly_fields
