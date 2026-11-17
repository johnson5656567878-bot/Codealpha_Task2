from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'liked your post'),
        ('comment', 'commented on your post'),
        ('follow', 'started following you'),
        ('reply', 'replied to your comment'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for @{self.recipient.username}: @{self.sender.username} {self.get_notification_type_display()}"

    @property
    def target_url(self):
        if self.post:
            return reverse('post_detail', kwargs={'pk': self.post.pk})
        elif self.notification_type == 'follow':
            return reverse('profile_view', kwargs={'username': self.sender.username})
        return reverse('notifications_view')

    @property
    def icon_class(self):
        icons = {
            'like': 'fa-solid fa-heart text-danger',
            'comment': 'fa-solid fa-comment text-primary',
            'follow': 'fa-solid fa-user-plus text-success',
            'reply': 'fa-solid fa-reply text-info',
        }
        return icons.get(self.notification_type, 'fa-solid fa-bell text-secondary')

def create_notification(recipient, sender, notification_type, post=None, comment=None):
    """Utility to safely create notifications, ignoring self-actions."""
    if recipient == sender:
        return None
    # For follows, avoid duplicate unread notifications
    if notification_type == 'follow':
        existing = Notification.objects.filter(recipient=recipient, sender=sender, notification_type='follow', is_read=False).first()
        if existing:
            return existing

    # For likes, avoid duplicate unread notifications for same post
    if notification_type == 'like' and post:
        existing = Notification.objects.filter(recipient=recipient, sender=sender, notification_type='like', post=post).first()
        if existing:
            return existing

    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        post=post,
        comment=comment
    )
