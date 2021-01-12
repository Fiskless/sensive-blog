from django.shortcuts import render
from django.db.models import Count

from blog.models import Comment, Post, Tag


def serialize_post(post):

    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_for_post_detail(post):

    post.comments_count = 1
    post_data = serialize_post(post)
    [post_data.pop(key) for key in ['teaser_text', 'comments_amount', 'first_tag_title']]
    comments = Comment.objects.prefetch_related('author').filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })
    new_data_for_posts = {'text': post.text, 'comments': serialized_comments, 'likes_amount': post.likes_count, }
    post_data.update(new_data_for_posts)

    return post_data


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.count_posts_for_tag,
    }


def index(request):

    most_popular_posts = Post.objects.get_prefetch_data_for_posts().\
                              prefetch_related('author').\
                              popular()[:5].\
                              fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5].get_count_posts_for_tag()

    most_fresh_posts = Post.objects.prefetch_related('author').\
                           get_prefetch_data_for_posts().\
                           order_by('-published_at')[:5].fetch_with_comments_count()

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):

    post = Post.objects.get_prefetch_data_for_posts().popular().get(slug=slug)

    most_popular_posts = Post.objects.prefetch_related('author'). \
                             get_prefetch_data_for_posts().\
                             popular()[:5].fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5].get_count_posts_for_tag()

    context = {
        'post': serialize_post_for_post_detail(post),
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_posts = Post.objects.prefetch_related('author'). \
                             get_prefetch_data_for_posts().\
                             popular()[:5].fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5].\
                            get_count_posts_for_tag()

    related_posts = Post.objects.prefetch_related('author'). \
                        get_prefetch_data_for_posts().\
                        fetch_with_comments_count()

    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})



