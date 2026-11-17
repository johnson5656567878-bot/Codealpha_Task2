def unread_notifications_count(request):
    """Adds unread notification count to context for authenticated users."""
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
