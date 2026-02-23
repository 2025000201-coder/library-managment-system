from .models import ActivityLog


def log_activity(user, action, description, request=None):
    """Helper function to create activity logs easily from any view."""
    ip = None
    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')

    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip
    )