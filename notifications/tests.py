from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from notifications.models import Notification, create_notification

class NotificationsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='u1', email='u1@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='u2', email='u2@example.com', password='Password123!')

    def test_notification_creation_and_mark_read(self):
        """Test notification creation and marking as read."""
        n = create_notification(recipient=self.user1, sender=self.user2, notification_type='follow')
        self.assertIsNotNone(n)
        self.assertFalse(n.is_read)

        self.client.login(username='u1', password='Password123!')

        # Check unread count
        count_res = self.client.get(reverse('api_notifications_unread_count'))
        self.assertEqual(count_res.json()['unread_count'], 1)

        # Mark as read
        read_res = self.client.post(reverse('api_mark_notification_read', kwargs={'pk': n.pk}))
        self.assertEqual(read_res.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_all_notifications_read(self):
        """Test bulk marking all notifications as read."""
        create_notification(recipient=self.user1, sender=self.user2, notification_type='follow')
        create_notification(recipient=self.user1, sender=self.user2, notification_type='like')

        self.client.login(username='u1', password='Password123!')
        res = self.client.post(reverse('api_mark_all_notifications_read'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.user1.notifications.filter(is_read=False).count(), 0)
