from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def notifications_view(request):
    filter_type = request.GET.get('filter', 'all')
    notifications = request.user.notifications.all().select_related('sender', 'sender__profile', 'post', 'comment')

    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type in ('like', 'comment', 'follow', 'reply'):
        notifications = notifications.filter(notification_type=filter_type)

    context = {
        'notifications': notifications[:50],
        'filter_type': filter_type,
    }
    return render(request, 'notifications.html', context)


@login_required
def api_unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})


@login_required
@require_POST
def api_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': unread_count})


@login_required
@require_POST
def api_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True, 'unread_count': 0})


@login_required
@require_POST
def api_delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.delete()
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': unread_count})
