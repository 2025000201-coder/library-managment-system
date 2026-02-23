from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {
            'fields': ('role', 'phone', 'address', 'profile_pic',
                       'membership_id', 'date_of_birth')
        }),
    )