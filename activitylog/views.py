from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ActivityLog, ACTION_ICONS


@login_required
def activity_log_list(request):
    if not request.user.is_admin_user:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')

    logs = ActivityLog.objects.select_related('user').all()

    # Filters
    search = request.GET.get('search', '')
    action_filter = request.GET.get('action', '')
    date_filter = request.GET.get('date', '')

    if search:
        logs = logs.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(description__icontains=search)
        )
    if action_filter:
        logs = logs.filter(action=action_filter)
    if date_filter:
        logs = logs.filter(timestamp__date=date_filter)

    # Add icon and color to each log
    logs_with_icons = []
    for log in logs[:200]:  # limit to 200 for performance
        icon, color = ACTION_ICONS.get(log.action, ('bi-activity', 'secondary'))
        logs_with_icons.append({
            'log': log,
            'icon': icon,
            'color': color,
        })

    context = {
        'logs': logs_with_icons,
        'search': search,
        'action_filter': action_filter,
        'date_filter': date_filter,
        'action_choices': ActivityLog.ACTION_CHOICES,
        'total_count': logs.count(),
    }
    return render(request, 'activitylog/activity_log.html', context)