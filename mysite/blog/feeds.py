"""
Feed module.
This module contains a feed class that provides RSS and Atom feeds for the blog.
"""

from django.db.models.base import Model
import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post


class LatestPostFeed(Feed):
    """
    A feed class that provides RSS and Atom feeds for the latest posts.
    Attributes:
        title (str): The title of the feed.
        link (str): The URL of the feed.
        description (str): A brief description of the feed.
    """

    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog'

    def items(self):
        """
        Returns a list of latest published posts.
        Returns:
            QuerySet: A query set of Post instances, limited to the first 5 instances.
        """
        return Post.published.all()[:5]

    def item_title(self, item):
        """
        Returns the title of an individual post.
        Args:
            item (Post): The Post instance.
        Returns:
            str: The title of the post.
        """
        return item.title

    def item_description(self, item):
        """
        Returns a truncated version of the body of an individual post.
        Args:
            item (Post): The Post instance.
        Returns:
            str: A truncated version of the post's body.
        """
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        """
        Returns the publication date of an individual post.
        Args:
            item (Post): The Post instance.
        Returns:
            datetime: The publication date of the post.
        """
        return item.publish
