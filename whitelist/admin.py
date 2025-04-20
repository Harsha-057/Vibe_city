from django.contrib import admin
from .models import WhitelistApplication
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages

@admin.register(WhitelistApplication)
class WhitelistApplicationAdmin(admin.ModelAdmin):
    list_display = ('discord_name', 'character_name', 'status', 'created_at', 'reviewed_at', 'action_buttons')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('discord_name', 'steam_name', 'steam_hex_id', 'character_name')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_applications', 'reject_applications', 'delete_selected']
    
    fieldsets = (
        ('Discord & Steam Information', {
            'fields': ('discord_name', 'steam_name', 'steam_hex_id', 'age')
        }),
        ('Server Information', {
            'fields': ('how_found', 'fivem_experience')
        }),
        ('Character Information', {
            'fields': ('character_name', 'character_age', 'character_backstory')
        }),
        ('Roleplay Knowledge', {
            'fields': ('fear_rp_explanation', 'fail_rp_explanation', 'robbery_response', 'rule_breaking_response')
        }),
        ('Rules & Status', {
            'fields': ('rules_acknowledged', 'status', 'feedback', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}" style="color: red;">Delete</a>',
            reverse('admin:whitelist_whitelistapplication_change', args=[obj.id]),
            reverse('admin:whitelist_whitelistapplication_delete', args=[obj.id])
        )
    action_buttons.short_description = 'Actions'
    
    @admin.action(description='Approve selected applications')
    def approve_applications(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        for application in queryset.filter(status='approved'):
            application.user.is_whitelisted = True
            application.user.save()
        self.message_user(request, f'Successfully approved {updated} applications.')
    
    @admin.action(description='Reject selected applications')
    def reject_applications(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        for application in queryset.filter(status='rejected'):
            application.user.is_whitelisted = False
            application.user.save()
        self.message_user(request, f'Successfully rejected {updated} applications.')
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status == 'approved':
                obj.user.is_whitelisted = True
                obj.user.save()
            elif obj.status == 'rejected':
                obj.user.is_whitelisted = False
                obj.user.save()
        super().save_model(request, obj, form, change)
