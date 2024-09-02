import markdown
from django.utils.safestring import mark_safe
from django import template
from ..models import Post
from django.db.models import Count


# Initialize the Django template library
register = template.Library()


@register.simple_tag
def total_posts():
    """
    Returns the total count of published posts.
    Returns:
        int: The total count of published posts.
    """
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """
    Displays the latest posts with a specified number of posts shown.
    Args:
        count (int, optional): The number of posts to display. Defaults to 5.
    Returns:
        dict: A dictionary containing the 'latest_posts' key with the latest posts as its value.
    """
    # Retrieve the latest posts in descending order, limited by the specified count
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    """
    Returns the most commented posts with a specified number of posts shown.
    Args:
        count (int, optional): The number of posts to display. Defaults to 5.
    Returns:
        QuerySet: A queryset containing the most commented posts.
    """
    # Annotate each post with the total count of comments and order by descending
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    """
    Formats the given text using markdown.
    Args:
        text (str): The text to be formatted.
    Returns:
        str: The formatted markdown text.
    """
    # Use mark_safe to safely render the markdown text as HTML
    return mark_safe(markdown.markdown(text))
