import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Post, PostImage, Like, Comment, Follow, Bookmark, Hashtag, Report, Block, PollOption, PollVote
from notifications.models import create_notification

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(file):
    """Validates image extension and file size."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type ({ext}). Allowed: JPG, PNG, WEBP, GIF."
    if file.size > MAX_FILE_SIZE:
        return False, f"File {file.name} exceeds the maximum size limit of 5MB."
    return True, None


@login_required
def home_feed_view(request):
    user = request.user

    # Exclude blocked users in both directions
    blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
    blocked_by_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
    excluded_user_ids = set(blocked_ids).union(set(blocked_by_ids))

    feed_type = request.GET.get('feed', 'for_you')

    if feed_type == 'following':
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        # Include followed accounts and own posts
        feed_user_ids = set(following_ids).union({user.id}) - excluded_user_ids
        posts_qs = Post.objects.filter(author_id__in=feed_user_ids)
    else:
        # For You: all posts excluding blocked users
        posts_qs = Post.objects.exclude(author_id__in=excluded_user_ids)

    posts_qs = posts_qs.select_related('author', 'author__profile').prefetch_related('images', 'likes', 'comments', 'hashtags')

    paginator = Paginator(posts_qs, 15)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    # Suggested users (exclude self, already followed, and blocked)
    following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    exclude_suggested = set(following_ids).union({user.id}).union(excluded_user_ids)
    suggested_users = User.objects.exclude(id__in=exclude_suggested).select_related('profile').annotate(
        follower_count=Count('follower_relations')
    ).order_by('-follower_count')[:5]

    # Trending hashtags
    trending_hashtags = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0).order_by('-post_count')[:6]

    context = {
        'posts': posts,
        'feed_type': feed_type,
        'suggested_users': suggested_users,
        'trending_hashtags': trending_hashtags,
    }
    return render(request, 'home.html', context)


def explore_view(request):
    excluded_user_ids = set()
    if request.user.is_authenticated:
        blocked_ids = Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
        blocked_by_ids = Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True)
        excluded_user_ids = set(blocked_ids).union(set(blocked_by_ids))

    # Explore shows popular and recent posts
    posts_qs = Post.objects.exclude(author_id__in=excluded_user_ids).select_related(
        'author', 'author__profile'
    ).prefetch_related('images', 'likes', 'comments').annotate(
        like_count=Count('likes')
    ).order_by('-like_count', '-created_at')

    paginator = Paginator(posts_qs, 20)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    trending_hashtags = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0).order_by('-post_count')[:10]

    context = {
        'posts': posts,
        'trending_hashtags': trending_hashtags,
    }
    return render(request, 'explore.html', context)


def search_view(request):
    query = request.GET.get('q', '').strip()
    tab = request.GET.get('type', 'all')  # all, users, posts, tags

    users = []
    posts = []
    hashtags = []

    if query:
        clean_tag_query = query.lstrip('#')
        
        # Search Users
        if tab in ('all', 'users'):
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).select_related('profile')[:20]

        # Search Posts
        if tab in ('all', 'posts'):
            posts = Post.objects.filter(
                Q(content__icontains=query) |
                Q(hashtags__name__icontains=clean_tag_query)
            ).distinct().select_related('author', 'author__profile').prefetch_related('images', 'likes', 'comments')[:20]

        # Search Hashtags
        if tab in ('all', 'tags'):
            hashtags = Hashtag.objects.filter(
                name__icontains=clean_tag_query
            ).annotate(post_count=Count('posts')).order_by('-post_count')[:15]

    context = {
        'query': query,
        'tab': tab,
        'users': users,
        'posts': posts,
        'hashtags': hashtags,
    }
    return render(request, 'search.html', context)


@login_required
def bookmarks_view(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related(
        'post', 'post__author', 'post__author__profile'
    ).prefetch_related('post__images', 'post__likes', 'post__comments')

    posts = [b.post for b in bookmarks]

    context = {
        'posts': posts,
    }
    return render(request, 'bookmarks.html', context)


def hashtag_posts_view(request, hashtag_name):
    clean_tag = hashtag_name.lower().strip()
    hashtag = get_object_or_404(Hashtag, name=clean_tag)
    posts = hashtag.posts.all().select_related('author', 'author__profile').prefetch_related('images', 'likes', 'comments')

    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)

    context = {
        'hashtag': hashtag,
        'posts': posts_page,
    }
    return render(request, 'posts/hashtag_posts.html', context)


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile').prefetch_related('images', 'likes', 'comments__author__profile', 'comments__replies__author__profile'),
        pk=pk
    )

    # Check if viewer blocked by author
    if request.user.is_authenticated:
        if Block.objects.filter(blocker=post.author, blocked=request.user).exists():
            return render(request, 'errors/403_blocked.html', status=403)

    # Top-level comments
    comments = post.comments.filter(parent__isnull=True).select_related('author', 'author__profile').prefetch_related('replies__author__profile')

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


# ========================================================
# AJAX / REST API ENDPOINTS
# ========================================================

@login_required
@require_POST
def api_create_post(request):
    content = request.POST.get('content', '').strip()
    post_type = request.POST.get('post_type', 'standard')
    code_snippet = request.POST.get('code_snippet', '').strip()
    code_language = request.POST.get('code_language', 'python').strip()
    badge_text = request.POST.get('badge_text', '').strip()
    badge_icon = request.POST.get('badge_icon', '').strip()
    poll_question = request.POST.get('poll_question', '').strip()
    images = request.FILES.getlist('images')

    if not content and not images and not code_snippet and not poll_question:
        return JsonResponse({'success': False, 'error': 'Post cannot be empty.'}, status=400)

    # Validate image files
    for img in images:
        valid, err_msg = validate_image_file(img)
        if not valid:
            return JsonResponse({'success': False, 'error': err_msg}, status=400)

    post = Post.objects.create(
        author=request.user,
        content=content,
        post_type=post_type,
        code_snippet=code_snippet,
        code_language=code_language,
        badge_text=badge_text,
        badge_icon=badge_icon,
        poll_question=poll_question
    )

    # Save images
    for img in images:
        PostImage.objects.create(post=post, image=img)

    # If poll post, create options
    if post_type == 'poll':
        # Poll options can be passed as poll_options[] or multiple poll_option inputs
        options = request.POST.getlist('poll_options[]') or request.POST.getlist('poll_options')
        if not options:
            # Fallback to comma/newline split if passed in a single textarea
            raw_opts = request.POST.get('poll_options_raw', '')
            options = [o.strip() for o in raw_opts.split('\n') if o.strip()]

        for idx, opt_text in enumerate(options[:6]):
            if opt_text.strip():
                PollOption.objects.create(post=post, text=opt_text.strip(), order=idx)

    return JsonResponse({
        'success': True,
        'message': 'Post published successfully!',
        'post_id': post.id,
        'redirect_url': post.get_absolute_url()
    })


@login_required
@require_POST
def api_vote_poll(request, pk):
    post = get_object_or_404(Post, pk=pk, post_type='poll')
    option_id = request.POST.get('option_id')
    option = get_object_or_404(PollOption, pk=option_id, post=post)

    # Update or create user vote
    vote, created = PollVote.objects.update_or_create(
        post=post,
        user=request.user,
        defaults={'option': option}
    )

    total_votes = post.total_poll_votes
    options_data = []
    for opt in post.poll_options.all():
        options_data.append({
            'id': opt.id,
            'text': opt.text,
            'votes_count': opt.votes_count,
            'percentage': opt.percentage(),
            'is_voted': opt.id == option.id
        })

    return JsonResponse({
        'success': True,
        'total_votes': total_votes,
        'options': options_data
    })


@login_required
@require_POST
def api_edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'You can only edit your own posts.'}, status=403)

    content = request.POST.get('content', '').strip()
    if not content and not post.images.exists():
        return JsonResponse({'success': False, 'error': 'Post content cannot be empty.'}, status=400)

    post.content = content
    post.save()

    return JsonResponse({
        'success': True,
        'message': 'Post updated successfully.',
        'formatted_content': post.formatted_content
    })


@login_required
@require_POST
def api_delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized.'}, status=403)

    post.delete()
    return JsonResponse({'success': True, 'message': 'Post deleted successfully.'})


@login_required
@require_POST
def api_toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
        create_notification(
            recipient=post.author,
            sender=request.user,
            notification_type='like',
            post=post
        )

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count
    })


def api_post_likes(request, pk):
    post = get_object_or_404(Post, pk=pk)
    likes = post.likes.select_related('user', 'user__profile')
    data = []
    for l in likes:
        is_following = False
        if request.user.is_authenticated:
            is_following = request.user.following_relations.filter(following=l.user).exists()
        data.append({
            'username': l.user.username,
            'display_name': l.user.profile.display_name,
            'avatar_url': l.user.profile.avatar_url,
            'is_following': is_following,
            'is_self': request.user == l.user
        })
    return JsonResponse({'users': data})


@login_required
@require_POST
def api_add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)

    parent_comment = None
    if parent_id:
        parent_comment = get_object_or_404(Comment, pk=parent_id, post=post)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent_comment
    )

    # Notifications
    if parent_comment:
        create_notification(
            recipient=parent_comment.author,
            sender=request.user,
            notification_type='reply',
            post=post,
            comment=comment
        )
    else:
        create_notification(
            recipient=post.author,
            sender=request.user,
            notification_type='comment',
            post=post,
            comment=comment
        )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'author': comment.author.username,
            'author_name': comment.author.profile.display_name,
            'author_avatar': comment.author.profile.avatar_url,
            'content': comment.formatted_content,
            'parent_id': parent_id,
            'created_at': 'Just now',
            'is_author': True
        },
        'comments_count': post.comments_count
    })


@login_required
@require_POST
def api_delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if comment.author != request.user and post.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized.'}, status=403)

    comment.delete()
    return JsonResponse({
        'success': True,
        'message': 'Comment removed.',
        'comments_count': post.comments_count
    })


@login_required
@require_POST
def api_toggle_bookmark(request, pk):
    post = get_object_or_404(Post, pk=pk)
    bookmark = Bookmark.objects.filter(user=request.user, post=post).first()

    if bookmark:
        bookmark.delete()
        bookmarked = False
    else:
        Bookmark.objects.create(user=request.user, post=post)
        bookmarked = True

    return JsonResponse({'success': True, 'bookmarked': bookmarked})


@login_required
@require_POST
def api_toggle_follow(request, username):
    target_user = get_object_or_404(User, username__iexact=username)
    if target_user == request.user:
        return JsonResponse({'success': False, 'error': 'You cannot follow yourself.'}, status=400)

    follow = Follow.objects.filter(follower=request.user, following=target_user).first()
    if follow:
        follow.delete()
        is_following = False
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True
        create_notification(
            recipient=target_user,
            sender=request.user,
            notification_type='follow'
        )

    return JsonResponse({
        'success': True,
        'is_following': is_following,
        'followers_count': target_user.follower_relations.count(),
        'following_count': target_user.following_relations.count()
    })


def api_get_followers(request, username):
    target_user = get_object_or_404(User, username__iexact=username)
    relations = target_user.follower_relations.select_related('follower', 'follower__profile')
    data = []
    for rel in relations:
        u = rel.follower
        is_following = False
        if request.user.is_authenticated:
            is_following = request.user.following_relations.filter(following=u).exists()
        data.append({
            'username': u.username,
            'display_name': u.profile.display_name,
            'avatar_url': u.profile.avatar_url,
            'bio': u.profile.bio[:80],
            'is_following': is_following,
            'is_self': request.user == u
        })
    return JsonResponse({'users': data})


def api_get_following(request, username):
    target_user = get_object_or_404(User, username__iexact=username)
    relations = target_user.following_relations.select_related('following', 'following__profile')
    data = []
    for rel in relations:
        u = rel.following
        is_following = False
        if request.user.is_authenticated:
            is_following = request.user.following_relations.filter(following=u).exists()
        data.append({
            'username': u.username,
            'display_name': u.profile.display_name,
            'avatar_url': u.profile.avatar_url,
            'bio': u.profile.bio[:80],
            'is_following': is_following,
            'is_self': request.user == u
        })
    return JsonResponse({'users': data})


@login_required
@require_POST
def api_report_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    reason = request.POST.get('reason', '').strip()
    details = request.POST.get('details', '').strip()

    if not reason:
        return JsonResponse({'success': False, 'error': 'Please select a reason for the report.'}, status=400)

    Report.objects.create(reporter=request.user, post=post, reason=reason, details=details)
    return JsonResponse({'success': True, 'message': 'Thank you. We have received your report and our team will review it.'})


@login_required
@require_POST
def api_toggle_block(request, username):
    target_user = get_object_or_404(User, username__iexact=username)
    if target_user == request.user:
        return JsonResponse({'success': False, 'error': 'You cannot block yourself.'}, status=400)

    block = Block.objects.filter(blocker=request.user, blocked=target_user).first()
    if block:
        block.delete()
        blocked = False
    else:
        Block.objects.create(blocker=request.user, blocked=target_user)
        # Clean up follow relationships
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        Follow.objects.filter(follower=target_user, following=request.user).delete()
        blocked = True

    return JsonResponse({'success': True, 'blocked': blocked})
