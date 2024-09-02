"""
Forms module.
This module contains form classes for search, comment and email post forms.
"""

from django import forms
from .models import Comment


class SearchForm(forms.Form):
    """
    A simple search form with a text input field.
    Attributes:
        query (forms.CharField): The search query field.
    """

    query = forms.CharField(
        # label="Search for posts",
        widget=forms.TextInput(attrs={"placeholder": "Search..."})
    )


class CommentForm(forms.ModelForm):
    """
    A model form for commenting on posts.
    Attributes:
        name (forms.CharField): The commenter's name.
        email (forms.EmailField): The commenter's email address.
        body (forms.CharField): The comment text.
    """

    class Meta:
        """
        Meta information for the CommentForm.
        Attributes:
            model (Comment): The underlying model instance.
            fields (list[str]): A list of field names to include in the form.
        """
        model = Comment
        fields = ['name', 'email', 'body']


class EmailPostForm(forms.Form):
    """
    An email post form with input fields for name, email and recipient's email.
    Attributes:
        name (forms.CharField): The sender's name.
        email (forms.EmailField): The sender's email address.
        to (forms.EmailField): The recipient's email address.
        comments (forms.CharField): Optional text comments.
    """

    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea
    )
