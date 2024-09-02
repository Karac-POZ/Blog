from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    """
    A sitemap class for the blog's posts.
    Attributes:
    changefreq (str): The frequency at which the post is changed.
    priority (float): The priority of the post in search engine results.
    items: A method to return a queryset of published posts.
    lastmod: A method to return the last modified date and time of each post.
    """

    changefreq = 'weekly'  # Posts are updated weekly
    priority = 0.9  # Posts have high priority in search engine results

    def items(self):
        """
        Returns a queryset of published posts.
        Returns:
        QuerySet: A queryset of published posts.
        """
        return Post.published.all()

    def lastmod(self, obj):
        """
        Returns the last modified date and time of each post.
        Args:
        obj (Post): The post object.
        Returns:
        datetime: The last modified date and time of the post.
        """
        return obj.updated
