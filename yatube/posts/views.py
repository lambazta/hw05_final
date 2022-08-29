import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

PER_PAGE = 10


def get_page_context(queryset, request):
    paginator = Paginator(queryset, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    context = get_page_context(post_list, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'post_list': post_list,
        'group': group,
    }
    context.update(get_page_context(post_list, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user.id,
            author=author.id
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'post_count': post_count,
        'following': following,
    }
    context.update(get_page_context(post_list, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author__exact=post.author).count()
    form = CommentForm(None)
    comments = post.comments.all()
    context = {
        'post': post,
        'post_count': post_count,
        'title': (f'Пост {post.text[:30]}'),
        'form': form,
        'comments': comments,

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.pub_date = datetime.datetime.now()
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        raise Http404("You are not allowed to edit this Post")
    is_edit = True
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'post': post, 'is_edit': is_edit}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    # Получите пост
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = get_page_context(post_list, request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    follow_author = get_object_or_404(User, username=username)
    follow_user = request.user
    if follow_author != follow_user:
        Follow.objects.get_or_create(
            user=follow_user, author=follow_author
        )
    return redirect('posts:profile', username=follow_author.username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    follow_author = get_object_or_404(User, username=username)
    follow_user = request.user
    if follow_author != follow_user:
        Follow.objects.filter(
            user=follow_user, author=follow_author
        ).delete()
    return redirect('posts:profile', username=follow_author.username)
