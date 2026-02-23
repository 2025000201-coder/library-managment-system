from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
    readonly_fields = ('user', 'action', 'description', 'timestamp', 'ip_address')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False  # Logs should only be created by the system