from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, default='')
    website = models.URLField(max_length=200, blank=True, default='')
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def display_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.username

    @property
    def avatar_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.svg'

    @property
    def cover_url(self):
        if self.cover_image and hasattr(self.cover_image, 'url'):
            return self.cover_image.url
        return '/static/images/default-cover.svg'

    @property
    def posts_count(self):
        return self.user.posts.count()

    @property
    def followers_count(self):
        # Follow model in posts app
        return self.user.follower_relations.count()

    @property
    def following_count(self):
        # Follow model in posts app
        return self.user.following_relations.count()

    def is_followed_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.user.follower_relations.filter(follower=user).exists()

    def get_absolute_url(self):
        return reverse('profile_view', kwargs={'username': self.user.username})
