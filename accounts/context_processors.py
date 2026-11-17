def user_profile_context(request):
    """Adds current user profile to template context if authenticated."""
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        return {'current_profile': profile}
    return {'current_profile': None}
