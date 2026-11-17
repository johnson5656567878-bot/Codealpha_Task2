from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('api/notifications/unread-count/', views.api_unread_count, name='api_notifications_unread_count'),
    path('api/notifications/<int:pk>/read/', views.api_mark_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.api_mark_all_read, name='api_mark_all_notifications_read'),
    path('api/notifications/<int:pk>/delete/', views.api_delete_notification, name='api_delete_notification'),
]
