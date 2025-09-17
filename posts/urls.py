from django.urls import path
from posts.views import feed, create_post, add_tags, like, delete_post, edit_post, friends_news

urlpatterns = [
    path('create-post/', create_post, name='create_post'),
    path('<int:post_id>/edit/', edit_post, name='edit_post'),
    path('delete-post/<int:post_id>/', delete_post, name='delete_post'),
    path('feed/', feed, name='feed'),
    path('friends-news/', friends_news, name='friends_news'),
    path('add-tags/<int:post_id>/', add_tags, name='add_tags'),
    path('<int:post_id>/like/', like, name='like'),
]
