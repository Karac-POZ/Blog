from django.shortcuts import get_object_or_404, render
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from .models import Post


def post_list(request, tag_slug=None):
    """
    A view function to display a list of posts.
    Args:
        request: The HTTP request object.
        tag_slug (str): The slug of the tag to filter by.
    Returns:
        render: A rendered template with the list of posts and optional tag information.
    """

    # Get the list of published posts
    post_list = Post.published.all()

    # Initialize the tag variable
    tag = None

    # If a tag slug is provided, get the corresponding tag object and filter the post list by it
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Create a paginator to split the post list into pages
    paginator = Paginator(post_list, 3)

    # Get the current page number from the request query string or default to 1
    page_number = request.GET.get('page', 1)

    try:
        # Attempt to get the requested page of posts
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If the page number is not an integer, return the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If the page number corresponds to an empty page, return the last page
        posts = paginator.page(paginator.num_pages)

    # Render the post list template with the requested posts and optional tag information
    return render(
        request,
        'blog/post/list.html',
        {
            'posts': posts,
            'tag': tag
        }
    )


def post_share(request, post_id):
    """
    A view function to handle sharing a post via email.
    Args:
        request: The HTTP request object.
        post_id (int): The ID of the post to share.
    Returns:
        render: A rendered template with the post and optional sent status information.
    """
    # Get the post object with the specified ID, checking that it's published
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    # Initialize a flag to track whether the email has been sent
    sent = False

    # Check if the request method is POST (i.e., the form has been submitted)
    if request.method == 'POST':
        # Create an instance of the EmailPostForm with the request data
        form = EmailPostForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Get the cleaned form data
            cd = form.cleaned_data

            # Get the absolute URL of the post
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )

            # Construct the email subject and body
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            # Send the email with the constructed subject and body
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )

            # Set the sent flag to True
            sent = True

    # If not POST, create an empty EmailPostForm instance
    else:
        form = EmailPostForm()

    # Render the post share template with the post and optional sent status information
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


def post_detail(request, year, month, day, post):
    """
    A view function to handle displaying the details of a specific blog post.
    Args:
        request (HttpRequest): The HTTP request object.
        year (int): The publication year of the post.
        month (int): The publication month of the post.
        day (int): The publication day of the post.
        post (str): The slug of the post to display.
    Returns:
        render: A rendered template with the post details, active comments,
            a comment form, and similar posts information.
    """

    # Get the post object with the specified ID, checking that it's published
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # Get a list of active comments for this post
    comments = post.comments.filter(active=True)

    # Create an instance of the comment form
    form = CommentForm()

    # Get the IDs of the tags associated with this post
    post_tags_ids = post.tags.values_list('id', flat=True)

    # Filter similar posts based on shared tags, excluding the current post
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)

    # Annotate and order the similar posts by the number of shared tags and publication date
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]

    # Render the post detail template with the required information
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts
        }
    )


@require_POST
def post_comment(request, post_id):
    """
    A view function to handle posting a comment on a specific blog post.
    Args:
        request (HttpRequest): The HTTP request object.
        post_id (int): The ID of the post where the comment will be posted.
    Returns:
        render: A rendered template with the post details, form, and newly created comment information.
    """

    # Get the post object with the specified ID, checking that it's published
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    # Initialize a variable to hold the newly created comment object
    comment = None

    # Create an instance of the comment form with data from the HTTP request
    form = CommentForm(data=request.POST)

    # Check if the form is valid (i.e., all required fields are filled correctly)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)

        # Assign the post to the comment
        comment.post = post

        # Save the comment to the database
        comment.save()

    # Render the comment template with the required information
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,  # The post where the comment was posted
            'form': form,  # The comment form used for posting a new comment
            'comment': comment  # The newly created comment object (if any)
        },
    )


def post_search(request):
    """
    A view function to handle search queries on blog posts.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        render: A rendered template with the search form, query, and search results.
    """

    # Initialize variables for the search form, query, and results
    form = SearchForm()
    query = None
    results = []

    # Check if a query is provided in the HTTP GET request
    if 'query' in request.GET:
        # Create an instance of the search form with data from the HTTP request
        form = SearchForm(request.GET)

        # Check if the form is valid (i.e., all required fields are filled correctly)
        if form.is_valid():
            # Extract the query from the cleaned form data
            query = form.cleaned_data['query']

            # Use TrigramSimilarity to search posts with a similarity score greater than 0.1
            results = (
                Post.published.annotate(
                    # Annotate each post object with a similarity value based on the query
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gt=0.1).order_by('-similarity')
            )

    # Render the search template with the required information
    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,  # The search form used for submitting a new query
            'query': query,  # The current query being searched (if any)
            'results': results  # A list of search results matching the query
        }
    )
