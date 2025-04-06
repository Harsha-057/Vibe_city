from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'discord_tag', 'is_whitelisted', 'is_staff_member',
        'is_staff', 'is_active', 
        'can_review_sasp', 'can_review_ems', 'can_review_mechanic'
    )
    list_filter = ('is_whitelisted', 'is_staff', 'is_active', 'can_review_sasp', 'can_review_ems', 'can_review_mechanic')
    search_fields = ('username', 'email', 'discord_username', 'discord_id')
    readonly_fields = ('discord_id', 'discord_username', 'discord_discriminator', 'discord_avatar')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Discord Info', {'fields': ('discord_id', 'discord_username', 'discord_discriminator', 'discord_avatar')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'is_whitelisted', 'is_staff_member',
                'can_review_sasp', 'can_review_ems', 'can_review_mechanic',
                'groups', 'user_permissions',
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
