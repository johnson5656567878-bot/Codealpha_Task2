from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Q

from .forms import UserRegistrationForm, UserProfileEditForm, CustomPasswordChangeForm
from .models import UserProfile
from posts.models import Post, Block, Follow

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Nexus, @{user.username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Check if login is via email or username
        user_obj = None
        if '@' in identifier:
            user_obj = User.objects.filter(email__iexact=identifier).first()
            if user_obj:
                identifier = user_obj.username

        user = authenticate(request, username=identifier, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f"Welcome back, @{user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('login')


def profile_view(request, username):
    target_user = get_object_or_404(User, username__iexact=username)
    profile = get_object_or_404(UserProfile, user=target_user)

    # Check if blocked
    is_blocked_by_viewer = False
    is_viewer_blocked = False
    if request.user.is_authenticated:
        is_blocked_by_viewer = Block.objects.filter(blocker=request.user, blocked=target_user).exists()
        is_viewer_blocked = Block.objects.filter(blocker=target_user, blocked=request.user).exists()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()

    # Get active tab: posts (default), media, likes
    tab = request.GET.get('tab', 'posts')

    user_posts = Post.objects.filter(author=target_user).prefetch_related('images', 'likes', 'comments', 'hashtags')
    if tab == 'media':
        posts = user_posts.filter(images__isnull=False).distinct()
    elif tab == 'likes':
        # Show posts liked by this user
        posts = Post.objects.filter(likes__user=target_user).prefetch_related('images', 'likes', 'comments', 'hashtags')
    else:
        posts = user_posts

    context = {
        'target_user': target_user,
        'profile': profile,
        'is_following': is_following,
        'is_self': request.user == target_user,
        'is_blocked_by_viewer': is_blocked_by_viewer,
        'is_viewer_blocked': is_viewer_blocked,
        'posts': posts,
        'active_tab': tab,
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def settings_view(request):
    user = request.user
    profile = user.profile

    profile_form = UserProfileEditForm(instance=profile)
    password_form = CustomPasswordChangeForm(user=user)

    active_section = request.GET.get('section', 'profile')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit_profile':
            profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('settings')
            else:
                active_section = 'profile'
                messages.error(request, "Failed to update profile. Check the errors.")

        elif action == 'change_password':
            password_form = CustomPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Your password has been changed. Please log in again if prompted.")
                login(request, user)  # Keep session active
                return redirect('settings')
            else:
                active_section = 'password'
                messages.error(request, "Failed to change password.")

    blocked_users = Block.objects.filter(blocker=user).select_related('blocked__profile')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'blocked_users': blocked_users,
        'active_section': active_section,
    }
    return render(request, 'profiles/settings.html', context)
