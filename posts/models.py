import re
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"

    @property
    def posts_count(self):
        return self.posts.count()

    def get_absolute_url(self):
        return reverse('hashtag_posts', kwargs={'hashtag_name': self.name})


class Post(models.Model):
    POST_TYPES = (
        ('standard', 'Standard Post'),
        ('poll', 'Interactive Poll'),
        ('code', 'Code Snippet'),
        ('announcement', 'Announcement & Milestone'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True)
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='standard')
    hashtags = models.ManyToManyField(Hashtag, related_name='posts', blank=True)

    # Code snippet fields
    code_snippet = models.TextField(blank=True, default='')
    code_language = models.CharField(max_length=30, blank=True, default='python')

    # Announcement / Milestone fields
    badge_text = models.CharField(max_length=50, blank=True, default='')
    badge_icon = models.CharField(max_length=50, blank=True, default='')

    # Poll question field
    poll_question = models.CharField(max_length=255, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        snippet = self.content[:30] + ('...' if len(self.content) > 30 else '')
        return f"Post ({self.post_type}) by @{self.author.username}: {snippet}"

    def extract_and_set_hashtags(self):
        """Extracts #hashtags from post content and updates the ManyToMany relationship."""
        hashtag_names = set(re.findall(r'#(\w+)', self.content))
        tags = []
        for name in hashtag_names:
            tag_clean = name.lower()
            tag_obj, _ = Hashtag.objects.get_or_create(name=tag_clean)
            tags.append(tag_obj)
        self.hashtags.set(tags)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.extract_and_set_hashtags()

    @property
    def formatted_content(self):
        """Converts hashtags and mentions to safe clickable links while escaping user input."""
        if not self.content:
            return ""
        escaped_text = escape(self.content)

        # Replace hashtags: #tag -> <a href="/tag/tag/">#tag</a>
        def replace_hashtag(match):
            tag = match.group(1)
            url = reverse('hashtag_posts', kwargs={'hashtag_name': tag.lower()})
            return f'<a href="{url}" class="hashtag-link">#{tag}</a>'

        formatted = re.sub(r'#(\w+)', replace_hashtag, escaped_text)

        # Replace mentions: @username -> <a href="/profile/username/">@username</a>
        def replace_mention(match):
            uname = match.group(1)
            url = reverse('profile_view', kwargs={'username': uname})
            return f'<a href="{url}" class="mention-link">@{uname}</a>'

        formatted = re.sub(r'@([a-zA-Z0-9_]+)', replace_mention, formatted)

        # Preserve line breaks
        formatted = formatted.replace('\n', '<br>')
        return mark_safe(formatted)

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def total_poll_votes(self):
        return self.poll_votes.count()

    def user_voted_option_id(self, user):
        if not user or not user.is_authenticated:
            return None
        vote = self.poll_votes.filter(user=user).first()
        return vote.option_id if vote else None

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def is_bookmarked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.bookmarked_by.filter(user=user).exists()

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})


class PollOption(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='poll_options')
    text = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Option '{self.text}' for Post #{self.post_id}"

    @property
    def votes_count(self):
        return self.votes.count()

    def percentage(self):
        total = self.post.total_poll_votes
        if total == 0:
            return 0
        return round((self.votes_count / total) * 100)


class PollVote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='poll_votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_post_poll_vote')
        ]

    def __str__(self):
        return f"@{self.user.username} voted on Post #{self.post_id}"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Post #{self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.user.username} liked Post #{self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by @{self.author.username} on Post #{self.post.id}"

    @property
    def formatted_content(self):
        escaped_text = escape(self.content)
        def replace_mention(match):
            uname = match.group(1)
            url = reverse('profile_view', kwargs={'username': uname})
            return f'<a href="{url}" class="mention-link">@{uname}</a>'
        formatted = re.sub(r'@([a-zA-Z0-9_]+)', replace_mention, escaped_text)
        return mark_safe(formatted.replace('\n', '<br>'))


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow_relation')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.follower.username} follows @{self.following.username}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_bookmark')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.user.username} saved Post #{self.post.id}"


class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_sent')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=100)
    details = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on Post #{self.post.id} by @{self.reporter.username}"


class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['blocker', 'blocked'], name='unique_user_block')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.blocker.username} blocked @{self.blocked.username}"
