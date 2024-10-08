from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from rest_framework.generics import get_object_or_404

from .models import Follow, Post, Comment, User
from django.shortcuts import render, redirect
from .forms import CommentForm, PostForm, UserEditForm


# Create your views here.

def post_list_view(request):
    posts = Post.objects.all().order_by('-created_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {'page_obj': page_obj})


def get_comment_count(post_id):
    cache_key = f'post_{post_id}_comment_count'
    count = cache.get(cache_key)
    return count


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Follow

@login_required
def post_detail_view(request, id):
    post = get_object_or_404(Post, id=id)
    comments = post.comments.all().order_by('-created_date')
    comment_count = get_comment_count(post.id)

    is_following = Follow.objects.filter(follower=request.user, following=post.author).exists()

    if request.method == 'POST':
 
        if 'follow' in request.POST:
            if not is_following and request.user != post.author:  
                Follow.objects.create(follower=request.user, following=post.author)
            return redirect('post_detail', id=post.id)
        elif 'unfollow' in request.POST:
            if is_following:
                Follow.objects.filter(follower=request.user, following=post.author).delete()
            return redirect('post_detail', id=post.id)
    
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', id=post.id)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_count': comment_count,
        'form': form,
        'is_following': is_following,  
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('post_list')

    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    following_users = user.following.all()
    followers = user.followers.all()

    return render(request, 'profile.html', {
        'user': user,
        'following_users': following_users,
        'followers': followers,
    })
@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('profile_view', user_id=user_to_follow.id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('profile_view', user_id=user_to_unfollow.id)


@login_required
def edit_user_view(request):
    user = request.user

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = UserEditForm(instance=user)

    return render(request, 'accounts/edit_user.html', {'form': form})
