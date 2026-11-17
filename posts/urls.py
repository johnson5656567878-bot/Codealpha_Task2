from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_feed_view, name='home'),
    path('explore/', views.explore_view, name='explore'),
    path('search/', views.search_view, name='search'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('tag/<str:hashtag_name>/', views.hashtag_posts_view, name='hashtag_posts'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),

    # API Endpoints
    path('api/posts/create/', views.api_create_post, name='api_create_post'),
    path('api/posts/<int:pk>/edit/', views.api_edit_post, name='api_edit_post'),
    path('api/posts/<int:pk>/delete/', views.api_delete_post, name='api_delete_post'),
    path('api/posts/<int:pk>/like/', views.api_toggle_like, name='api_toggle_like'),
    path('api/posts/<int:pk>/likes/', views.api_post_likes, name='api_post_likes'),
    path('api/posts/<int:pk>/comments/', views.api_add_comment, name='api_add_comment'),
    path('api/comments/<int:pk>/delete/', views.api_delete_comment, name='api_delete_comment'),
    path('api/posts/<int:pk>/bookmark/', views.api_toggle_bookmark, name='api_toggle_bookmark'),
    path('api/posts/<int:pk>/vote/', views.api_vote_poll, name='api_vote_poll'),
    path('api/posts/<int:pk>/report/', views.api_report_post, name='api_report_post'),
    path('api/users/<str:username>/follow/', views.api_toggle_follow, name='api_toggle_follow'),
    path('api/users/<str:username>/followers/', views.api_get_followers, name='api_get_followers'),
    path('api/users/<str:username>/following/', views.api_get_following, name='api_get_following'),
    path('api/users/<str:username>/block/', views.api_toggle_block, name='api_toggle_block'),
]
