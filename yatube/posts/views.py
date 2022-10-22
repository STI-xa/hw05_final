from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import paginator_function

User = get_user_model()


@login_required
def follow_index(request):
    follower = Follow.objects.filter(user=request.user).values_list(
        'author_id', flat=True
    )
    posts = Post.objects.filter(author_id__in=follower)
    context = {
        'page_obj': paginator_function(posts, request),
    }
    return render(request, 'posts/follow_index.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(
        user=request.user,
        author=author
    ).exists() and request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username
    ).delete()
    return redirect('posts:follow_index')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user != post.author:
        return redirect('posts:post_detail', pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk)
    else:
        return render(
            request,
            'posts/create_post.html', {'form': form, 'is_edit': True}
        )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = author.following.exists()
    context = {
        'author': author,
        'page_obj': paginator_function(posts, request),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginator_function(posts, request),
    }

    return render(request, 'posts/group_list.html', context)


def index(request):
    posts = Post.objects.all()
    context = {
        'page_obj': paginator_function(posts, request),
    }
    return render(request, 'posts/index.html', context)
