from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """
    A custom manager to retrieve published posts only.
    Returns a QuerySet of all posts with their status set to 'PUBLISHED'.
    """

    def get_queryset(self):
        """
        Get the queryset of published posts.
        Returns:
            QuerySet: A queryset containing all published posts.
        """
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )


class Post(models.Model):
    """
    A model representing a blog post.
    Attributes:
        title (str): The title of the post.
        slug (str): The unique slug for the post.
        author (User): The user who authored the post.
        body (str): The content of the post.
        publish (datetime): The date and time when the post was published.
        created (datetime): The date and time when the post was created.
        updated (datetime): The date and time when the post was last updated.
        status (str): The status of the post (draft or published).
    """

    class Status(models.TextChoices):
        """
        An enumeration of possible statuses for a post.
        Attributes:
            DRAFT (str): The 'Draft' status.
            PUBLISHED (str): The 'Published' status.
        """
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        unique_for_date='publish')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class Meta:
        """
        Metadata for this model.
        Attributes:
            ordering (list): The default ordering for posts.
            indexes (list): The indexes to create on the 'publish' field.
        """
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        """
        A string representation of this post.
        Returns:
            str: The title of the post.
        """
        return self.title

    def get_absolute_url(self):
        """
        Get the absolute URL for this post.
        Returns:
            str: The absolute URL for this post.
        """
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )


class Comment(models.Model):
    """
    A model representing a comment made on a post.
    Attributes:
    post (Post): The post that this comment is associated with.
    name (str): The name of the person who made the comment.
    email (str): The email address of the person who made the comment.
    body (str): The text content of the comment.
    created (datetime): The date and time when the comment was created.
    updated (datetime): The date and time when the comment was last updated.
    active (bool): A flag indicating whether the comment is still active.
    Meta:
    ordering: The default order in which comments should be displayed.
    indexes: An index to speed up queries based on the 'created' field.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
