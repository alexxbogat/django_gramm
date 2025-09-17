from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from posts.models import Post, Like
from posts.forms import PostForm, AddTagsForm
from posts.utils import parse_and_add_tags
from photos.models import PostImage


@login_required
def create_post(request):
    """Handle creation of a new post by an authenticated user."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            tag_string = form.cleaned_data.get('tags', '')
            parse_and_add_tags(tag_string, post)
            for image in images:
                PostImage.objects.create(file=image, uploaded_by=request.user, post=post)
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def edit_post(request, post_id: int):
    """Allow the post owner to edit an existing post."""
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        return HttpResponseForbidden('You cannot edit this post.')
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        images = request.FILES.getlist('images')
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.user = request.user
            updated_post.save()

            tag_string = form.cleaned_data.get('tags', '')
            post.tags.clear()
            parse_and_add_tags(tag_string, post)

            delete_ids = request.POST.getlist("delete_images")
            if delete_ids:
                PostImage.objects.filter(id__in=delete_ids, post=post).delete()

            for image in images:
                PostImage.objects.create(file=image, uploaded_by=request.user, post=post)
            return redirect('profile', username=request.user.username)
    else:
        tags_string = ", ".join(tag.name for tag in post.tags.all())
        form = PostForm(instance=post, initial={'tags': tags_string})
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id: int):
    """Delete a post owned by the current user."""
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        return HttpResponseForbidden('You cannot delete this post.')
    if request.method == 'POST':
        post.delete()
        return redirect(request.META.get('HTTP_REFERER', 'profile'))


@login_required
def add_tags(request, post_id: int):
    """Adds tags to an existing post."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = AddTagsForm(request.POST)
        if form.is_valid():
            tag_string = form.cleaned_data['tags']
            parse_and_add_tags(tag_string, post)
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


@login_required
def like(request, post_id: int):
    """Toggles the like status for a post by the current user."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count(), 'success': True})


@login_required
def feed(request):
    """Display the feed page with posts ordered by creation date descending."""
    posts = (Post.objects.select_related('user__profile')
             .prefetch_related('tags', 'images',
                               Prefetch('likes', queryset=Like.objects.filter(user=request.user),
                                        to_attr='liked_by_user')).order_by('-created_at'))

    return render(request, 'posts/feed.html', {'posts': posts})


@login_required
def friends_news(request):
    """Render a feed of posts from users that the current authenticated user is following."""
    following_ids = request.user.following.values_list('user', flat=True)
    posts = (Post.objects
             .filter(user_id__in=following_ids)
             .select_related('user__profile')
             .prefetch_related('tags', 'images',
                               Prefetch('likes', queryset=Like.objects.filter(user=request.user),
                                        to_attr='liked_by_user')).order_by('-created_at'))

    return render(request, 'posts/friends_news.html', {'posts': posts})
