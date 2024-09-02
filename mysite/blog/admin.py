"""
Models admin interface configuration.
This module contains Django admin configurations for Post and Comment models.
"""

from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Configuration for Post model admin interface.
    Attributes:
        list_display (list): List of fields to display in the admin list view.
        list_filter (list): List of fields to use as filters in the admin list view.
        search_fields (list): List of fields to search in the admin list view.
        prepopulated_fields (dict): Fields that are populated automatically when creating a new instance.
        raw_id_fields (list): Fields that are displayed as raw IDs in the admin list view.
        date_hierarchy (str): Date hierarchy for filtering and ordering data.
        ordering (list): Default ordering of instances in the admin list view.
        show_facets (int): Whether to display facets in the admin list view.

    """
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Configuration for Comment model admin interface.
    Attributes:
        list_display (list): List of fields to display in the admin list view.
        list_filter (list): List of fields to use as filters in the admin list view.
        search_fields (list): List of fields to search in the admin list view.

    """
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
