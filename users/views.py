from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from posts.models import Post
from users.models import Followers
from users.forms import UserInfoForm, UserLoginForm, UserProfileForm, UserRegisterForm
from users.utils import send_verification_email
from photos.models import AvatarImage

User = get_user_model()


def login(request):
    """Authenticates a user and logs them in if the credentials are valid and email is verified."""
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.email_verified:
                    auth.login(request, user)
                    return redirect('feed')
                else:
                    form.add_error(None, "Email not verified.")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout(request):
    """Logs out the currently authenticated user and redirects to the login page."""
    auth.logout(request)
    return redirect('login')


def register(request):
    """Handles user registration."""
    if request.user.is_authenticated:
        return redirect('feed')
    email_sent = False
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(request, user)
            email_sent = True
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {
        'form': form,
        'email_sent': email_sent,
    })


def activate(request, uidb64: str, token: str):
    """Activates a user account via email verification link.

    Args:
        uidb64: Base64 encoded user ID.
        token: Token used to validate the user.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session['email_verified_success'] = True
        return redirect('edit_profile', username=user.username)
    return render(request, 'users/register.html')


@login_required
def profile(request, username: str):
    """Displays the profile page of a user with their posts."""
    user = get_object_or_404(User, username=username)
    is_following = Followers.objects.filter(follower=request.user, user=user).exists()
    posts = Post.objects.filter(user=user).prefetch_related('images', 'tags', 'likes').order_by('-created_at')
    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()
    return render(request, 'users/profile.html', {
        'user': user,
        'is_owner': request.user == user,
        'posts': posts,
        'is_following': is_following,
    })


@login_required
def edit_profile(request, username: str):
    """Allows the logged-in user to edit their profile."""
    if request.user.username != username:
        return redirect('profile', username=request.user.username)

    profile = request.user.profile

    if request.method == 'POST':
        user_form = UserInfoForm(instance=request.user, data=request.POST)
        profile_form = UserProfileForm(instance=profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                if profile.avatar:
                    profile.avatar.file = avatar_file
                    profile.avatar.uploaded_by = request.user
                    profile.avatar.save()
                else:
                    avatar = AvatarImage.objects.create(file=avatar_file, uploaded_by=request.user)
                    profile.avatar = avatar

            profile.save()
            request.session['profile_updated'] = True
    else:
        user_form = UserInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    show_success = request.session.pop('email_verified_success', False)
    show_success_profile = request.session.pop('profile_updated', False)

    return render(request, 'users/edit_profile.html', {
        'show_success': show_success,
        'show_success_profile': show_success_profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'username': username
    })


@login_required
def subscribe(request, user_id: int):
    """Subscribe or unsubscribe the authenticated user to/from the target user."""
    target_user = get_object_or_404(User, id=user_id)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if target_user == request.user:
        return JsonResponse({'success': False, 'error': 'Cannot subscribe to yourself'})

    follower_subscriber, created = Followers.objects.get_or_create(user=target_user, follower=request.user)
    if not created:
        follower_subscriber.delete()
        following = False
    else:
        following = True
    return JsonResponse({'following': following, 'followers_count': target_user.followers.count(), 'success': True})


@login_required
def followers_list(request, username):
    """Display a list of users who are following the specified user."""
    user = get_object_or_404(User, username=username)
    followers = [f.follower for f in user.followers.all()]
    return render(request, "users/followers_list.html", {
        "users": followers,
        "profile_user": user,
        "title": "Followers"
    })


@login_required
def following_list(request, username):
    """Display a list of users that the specified user is following."""
    user = get_object_or_404(User, username=username)
    following = [f.user for f in user.following.all()]
    return render(request, "users/followers_list.html", {
        "users": following,
        "profile_user": user,
        "title": "Following"
    })
