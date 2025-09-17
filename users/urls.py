from django.urls import path, include
from users.views import (login, register, profile,
                         edit_profile, activate, logout,
                         subscribe, followers_list, following_list)

urlpatterns = [
    path('auth/', include('social_django.urls', namespace='social')),
    path('', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('profile/<str:username>/', profile, name='profile'),
    path('profile/<str:username>/edit/', edit_profile, name='edit_profile'),
    path('<int:user_id>/subscribe/', subscribe, name='subscribe'),
    path('profile/<str:username>/followers/', followers_list, name='followers_list'),
    path('profile/<str:username>/following/', following_list, name='following_list'),
]
