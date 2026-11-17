from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from posts.models import Post, Hashtag, Like, Comment, Follow, Bookmark, Block
from notifications.models import Notification

class PostsAndInteractionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='Password123!')

    def test_post_creation_and_hashtag_extraction(self):
        """Test post creation automatically extracts hashtags."""
        self.client.login(username='alice', password='Password123!')
        res = self.client.post(reverse('api_create_post'), {
            'content': 'Hello world! This is my first #django app with #python and #webdev.'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user1)
        self.assertEqual(post.hashtags.count(), 3)
        self.assertTrue(Hashtag.objects.filter(name='django').exists())

    def test_post_edit_by_author_and_stranger(self):
        """Test author can edit own post, but stranger cannot."""
        post = Post.objects.create(author=self.user1, content='Original content')

        # Stranger attempts edit
        self.client.login(username='bob', password='Password123!')
        fail_res = self.client.post(reverse('api_edit_post', kwargs={'pk': post.pk}), {
            'content': 'Hacked content'
        })
        self.assertEqual(fail_res.status_code, 403)
        post.refresh_from_db()
        self.assertEqual(post.content, 'Original content')

        # Author edits
        self.client.login(username='alice', password='Password123!')
        ok_res = self.client.post(reverse('api_edit_post', kwargs={'pk': post.pk}), {
            'content': 'Updated content'
        })
        self.assertEqual(ok_res.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.content, 'Updated content')

    def test_post_delete_by_author_and_stranger(self):
        """Test author can delete own post, but stranger cannot."""
        post = Post.objects.create(author=self.user1, content='Post to delete')

        # Stranger attempts delete
        self.client.login(username='bob', password='Password123!')
        fail_res = self.client.post(reverse('api_delete_post', kwargs={'pk': post.pk}))
        self.assertEqual(fail_res.status_code, 403)
        self.assertEqual(Post.objects.count(), 1)

        # Author deletes
        self.client.login(username='alice', password='Password123!')
        ok_res = self.client.post(reverse('api_delete_post', kwargs={'pk': post.pk}))
        self.assertEqual(ok_res.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)

    def test_like_and_unlike_toggle(self):
        """Test liking and unliking a post, and notification generation."""
        post = Post.objects.create(author=self.user1, content='Like me')
        self.client.login(username='bob', password='Password123!')

        # 1. Like
        res1 = self.client.post(reverse('api_toggle_like', kwargs={'pk': post.pk}))
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertTrue(data1['liked'])
        self.assertEqual(data1['likes_count'], 1)
        self.assertEqual(Like.objects.count(), 1)

        # Verify notification created for alice
        self.assertTrue(Notification.objects.filter(recipient=self.user1, sender=self.user2, notification_type='like').exists())

        # 2. Unlike
        res2 = self.client.post(reverse('api_toggle_like', kwargs={'pk': post.pk}))
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertFalse(data2['liked'])
        self.assertEqual(data2['likes_count'], 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_comment_and_delete(self):
        """Test adding and deleting comments."""
        post = Post.objects.create(author=self.user1, content='Post for comments')
        self.client.login(username='bob', password='Password123!')

        # Add comment
        res = self.client.post(reverse('api_add_comment', kwargs={'pk': post.pk}), {
            'content': 'This is a great thought!'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(post.comments.count(), 1)
        comment = post.comments.first()
        self.assertEqual(comment.author, self.user2)

        # Delete comment
        del_res = self.client.post(reverse('api_delete_comment', kwargs={'pk': comment.pk}))
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(post.comments.count(), 0)

    def test_follow_and_unfollow(self):
        """Test follow and unfollow toggle, and self-follow prevention."""
        self.client.login(username='alice', password='Password123!')

        # Cannot follow self
        self_res = self.client.post(reverse('api_toggle_follow', kwargs={'username': 'alice'}))
        self.assertEqual(self_res.status_code, 400)
        self.assertEqual(Follow.objects.count(), 0)

        # Follow bob
        follow_res = self.client.post(reverse('api_toggle_follow', kwargs={'username': 'bob'}))
        self.assertEqual(follow_res.status_code, 200)
        self.assertTrue(follow_res.json()['is_following'])
        self.assertEqual(self.user2.follower_relations.count(), 1)
        self.assertEqual(self.user1.following_relations.count(), 1)

        # Unfollow bob
        unfollow_res = self.client.post(reverse('api_toggle_follow', kwargs={'username': 'bob'}))
        self.assertEqual(unfollow_res.status_code, 200)
        self.assertFalse(unfollow_res.json()['is_following'])
        self.assertEqual(self.user2.follower_relations.count(), 0)

    def test_search_users_and_posts(self):
        """Test search query returns matched users and posts."""
        Post.objects.create(author=self.user1, content='Designing futuristic interfaces')
        self.client.login(username='bob', password='Password123!')

        res = self.client.get(reverse('search') + '?q=design')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Designing futuristic interfaces')

    def test_create_and_vote_poll(self):
        """Test creating a poll and casting a vote."""
        self.client.login(username='alice', password='Password123!')
        res = self.client.post(reverse('api_create_post'), {
            'content': 'Vote on this poll!',
            'post_type': 'poll',
            'poll_question': 'Favorite fruit?',
            'poll_options[]': ['Apple', 'Banana', 'Orange']
        })
        self.assertEqual(res.status_code, 200)
        post = Post.objects.filter(post_type='poll').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.poll_options.count(), 3)

        # Bob votes for Banana
        self.client.login(username='bob', password='Password123!')
        banana_opt = post.poll_options.filter(text='Banana').first()
        vote_res = self.client.post(reverse('api_vote_poll', kwargs={'pk': post.pk}), {
            'option_id': banana_opt.id
        })
        self.assertEqual(vote_res.status_code, 200)
        data = vote_res.json()
        self.assertEqual(data['total_votes'], 1)
        self.assertEqual(banana_opt.votes_count, 1)

    def test_create_code_snippet_post(self):
        """Test creating a code snippet post."""
        self.client.login(username='alice', password='Password123!')
        res = self.client.post(reverse('api_create_post'), {
            'content': 'Here is some code',
            'post_type': 'code',
            'code_language': 'python',
            'code_snippet': 'print("Hello from Nexus!")'
        })
        self.assertEqual(res.status_code, 200)
        post = Post.objects.filter(post_type='code').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.code_language, 'python')
        self.assertIn('print("Hello from Nexus!")', post.code_snippet)
