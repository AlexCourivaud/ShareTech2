from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Interface d'administration pour les utilisateurs"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    # Ajout du champ role dans les formulaires
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations ShareTech', {
            'fields': ('role', 'avatar_url')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations ShareTech', {
            'fields': ('role', 'avatar_url')
        }),
    )