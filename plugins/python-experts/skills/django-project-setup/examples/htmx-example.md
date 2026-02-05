# HTMX Integration Example

This project uses django-htmx for modern frontend interactivity without complex JavaScript frameworks.

## Basic HTMX View Pattern

**apps/blog/views.py**:

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from apps.blog.models import Post


def post_list(request):
    """List posts with HTMX support."""
    posts = Post.objects.filter(published=True)

    if request.htmx:
        # Return partial template for HTMX requests
        return render(request, 'blog/partials/post_list.html', {'posts': posts})

    # Return full page for regular requests
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    """Post detail with HTMX comments."""
    post = get_object_or_404(Post, slug=slug, published=True)
    comments = post.comments.all()

    if request.htmx:
        return render(request, 'blog/partials/post_detail.html', {
            'post': post,
            'comments': comments
        })

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments
    })
```

## Full Page Template

**templates/blog/post_list.html**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Posts</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        .htmx-indicator { opacity: 0; transition: opacity 200ms ease-in; }
        .htmx-request .htmx-indicator { opacity: 1; }
        .htmx-request.htmx-indicator { opacity: 1; }
    </style>
</head>
<body>
    <div id="content">
        {% include 'blog/partials/post_list.html' %}
    </div>
</body>
</html>
```

## Partial Template

**templates/blog/partials/post_list.html**:

```html
<h1>Blog Posts</h1>

<div class="posts">
    {% for post in posts %}
    <article class="post">
        <h2>
            <a href="{% url 'blog:post_detail' post.slug %}"
               hx-get="{% url 'blog:post_detail' post.slug %}"
               hx-target="#content"
               hx-push-url="true">
                {{ post.title }}
            </a>
        </h2>
        <p>{{ post.content|truncatewords:30 }}</p>
        <small>By {{ post.author.username }} on {{ post.created_at|date:"M d, Y" }}</small>
    </article>
    {% endfor %}
</div>
```

## Form Submission with HTMX

**apps/blog/views.py**:

```python
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["POST"])
def add_comment(request, slug):
    """Add comment via HTMX."""
    post = get_object_or_404(Post, slug=slug)
    content = request.POST.get('content', '').strip()

    if not content:
        return HttpResponse(
            '<div class="error">Comment cannot be empty</div>',
            status=400
        )

    comment = post.comments.create(
        author=request.user,
        content=content
    )

    # Return the new comment HTML
    return render(request, 'blog/partials/comment.html', {
        'comment': comment
    })
```

**templates/blog/partials/comment_form.html**:

```html
<form hx-post="{% url 'blog:add_comment' post.slug %}"
      hx-target="#comments"
      hx-swap="afterbegin"
      hx-on::after-request="this.reset()">
    {% csrf_token %}
    <textarea name="content"
              placeholder="Add a comment..."
              required></textarea>
    <button type="submit">Post Comment</button>
    <div class="htmx-indicator">Posting...</div>
</form>
```

**templates/blog/partials/comment.html**:

```html
<div class="comment" id="comment-{{ comment.id }}">
    <strong>{{ comment.author.username }}</strong>
    <p>{{ comment.content }}</p>
    <small>{{ comment.created_at|date:"M d, Y H:i" }}</small>
    {% if comment.author == request.user %}
    <button hx-delete="{% url 'blog:delete_comment' comment.id %}"
            hx-target="#comment-{{ comment.id }}"
            hx-swap="outerHTML"
            hx-confirm="Delete this comment?">
        Delete
    </button>
    {% endif %}
</div>
```

## Infinite Scroll Pattern

**apps/blog/views.py**:

```python
from django.core.paginator import Paginator


def post_list_infinite(request):
    """Infinite scroll post list."""
    posts = Post.objects.filter(published=True)
    page = request.GET.get('page', 1)

    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page)

    if request.htmx:
        return render(request, 'blog/partials/post_list_infinite.html', {
            'page_obj': page_obj
        })

    return render(request, 'blog/post_list_infinite.html', {
        'page_obj': page_obj
    })
```

**templates/blog/partials/post_list_infinite.html**:

```html
{% for post in page_obj %}
<article class="post">
    <h2>{{ post.title }}</h2>
    <p>{{ post.content|truncatewords:30 }}</p>
</article>
{% endfor %}

{% if page_obj.has_next %}
<div hx-get="?page={{ page_obj.next_page_number }}"
     hx-trigger="revealed"
     hx-swap="outerHTML">
    <div class="htmx-indicator">Loading more...</div>
</div>
{% endif %}
```

## Search with Debounce

**apps/blog/views.py**:

```python
from django.db.models import Q


def search_posts(request):
    """Search posts with HTMX."""
    query = request.GET.get('q', '').strip()

    if not query:
        posts = Post.objects.filter(published=True)[:10]
    else:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            published=True
        )[:10]

    return render(request, 'blog/partials/search_results.html', {
        'posts': posts,
        'query': query
    })
```

**templates/blog/search.html**:

```html
<input type="search"
       name="q"
       placeholder="Search posts..."
       hx-get="{% url 'blog:search' %}"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#search-results"
       hx-indicator="#search-indicator">

<div id="search-indicator" class="htmx-indicator">Searching...</div>

<div id="search-results">
    <!-- Results will appear here -->
</div>
```

## Delete with Confirmation

**apps/blog/views.py**:

```python
@login_required
@require_http_methods(["DELETE"])
def delete_comment(request, comment_id):
    """Delete comment via HTMX."""
    comment = get_object_or_404(Comment, id=comment_id)

    # Check permission
    if comment.author != request.user and not request.user.is_staff:
        return HttpResponse(status=403)

    comment.delete()

    # Return empty response (element will be removed by hx-swap)
    return HttpResponse(status=200)
```

## Loading States

Add CSS for loading indicators:

```css
/* Global loading indicator */
.htmx-indicator {
    opacity: 0;
    transition: opacity 200ms ease-in;
}

.htmx-request .htmx-indicator {
    opacity: 1;
}

.htmx-request.htmx-indicator {
    opacity: 1;
}

/* Disabled state for forms */
.htmx-request button {
    opacity: 0.6;
    cursor: not-allowed;
}
```

## Error Handling

**apps/blog/views.py**:

```python
from django.views.decorators.http import require_POST


@require_POST
def like_post(request, slug):
    """Like post with error handling."""
    try:
        post = get_object_or_404(Post, slug=slug)

        # Toggle like
        if request.user in post.liked_by.all():
            post.liked_by.remove(request.user)
            liked = False
        else:
            post.liked_by.add(request.user)
            liked = True

        return render(request, 'blog/partials/like_button.html', {
            'post': post,
            'liked': liked
        })

    except Exception as e:
        return HttpResponse(
            f'<div class="error">Error: {str(e)}</div>',
            status=500
        )
```

## HTMX Best Practices

1. **Progressive Enhancement**: Always provide full page fallback
2. **Security**: Use CSRF tokens in all POST/DELETE forms
3. **Performance**: Use `hx-trigger="revealed"` for infinite scroll
4. **UX**: Add loading indicators with `htmx-indicator` class
5. **Testing**: Test both HTMX and non-HTMX paths
6. **SEO**: Use `hx-push-url` to update URL for navigation

## Testing HTMX Views

```python
import pytest
from django.test import Client


@pytest.mark.django_db
class TestHTMXViews:
    def test_post_list_full_page(self, client):
        """Test full page request."""
        response = client.get('/blog/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.content

    def test_post_list_htmx(self, client):
        """Test HTMX partial request."""
        response = client.get('/blog/', HTTP_HX_REQUEST='true')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' not in response.content

    def test_add_comment_htmx(self, authenticated_client, post):
        """Test adding comment via HTMX."""
        response = authenticated_client.post(
            f'/blog/{post.slug}/comments/',
            {'content': 'Test comment'},
            HTTP_HX_REQUEST='true'
        )
        assert response.status_code == 200
        assert b'Test comment' in response.content
```
