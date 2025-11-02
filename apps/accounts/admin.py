# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _
import re

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'formatted_cpf', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'user_type', 'is_superuser')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'user_type', 'cpf')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'cpf', 'first_name', 'last_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('email', 'cpf', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    @admin.display(description='CPF')
    def formatted_cpf(self, obj):
        """Exibe o CPF no formato 000.000.000-00"""
        if not obj.cpf:
            return ''
        cpf = re.sub(r'\D', '', obj.cpf)
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
