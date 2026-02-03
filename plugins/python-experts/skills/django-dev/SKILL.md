---
name: django
description: Django development patterns and conventions (2025). Auto-loads when working with Django models, views, URLs, forms, templates, management commands, or project structure. Includes async support and type hints.
user-invocable: false
---

# Django Development (2025)

## Project Structure

```
project_name/
├── config/                 # Project config (rename from project_name/)
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py             # Required for async
├── apps/
│   ├── __init__.py
│   └── core/               # Shared utilities, base models
├── templates/
├── static/
├── manage.py
├── pyproject.toml          # Modern Python packaging
└── requirements/
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

## Environment & Settings

```python
# config/settings/base.py
import environ

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env()

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
DATABASES = {"default": env.db()}
```

```bash
# .env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
```

## Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| App | singular, lowercase | `blog`, `user_profile` |
| Model | singular PascalCase | `Article`, `UserProfile` |
| View (function) | `noun_action` | `article_detail` |
| View (class) | `NounActionView` | `ArticleDetailView` |
| URL name | `app:noun-action` | `blog:article-detail` |
| Template | `app/noun_action.html` | `blog/article_detail.html` |

## Models

```python
from django.db import models
from django.urls import reverse


class TimestampedModel(models.Model):
    """Abstract base for created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Article(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("blog:article-detail", kwargs={"slug": self.slug})
```

**Key patterns:**
- Use `TextChoices` / `IntegerChoices` for choices (not tuples)
- Type hints on methods
- Always set `related_name`, `db_index` on filtered fields

## Views

### Sync Views (Standard)

```python
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("author")
        if q := self.request.GET.get("q"):
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
        return qs
```

### Async Views

Use async for I/O-bound operations (external APIs, file ops). Requires ASGI server.

```python
import httpx
from django.http import JsonResponse
from asgiref.sync import sync_to_async


async def weather_view(request):
    """Async view calling external API."""
    city = request.GET.get("city", "London")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
    return JsonResponse(response.json())


async def article_list_async(request):
    """Async view with ORM (requires sync_to_async wrapper)."""
    articles = await sync_to_async(list)(
        Article.objects.select_related("author")[:20]
    )
    return JsonResponse({"articles": [a.title for a in articles]})
```

**When to use async views:**
- External HTTP calls → use `httpx` (async) not `requests`
- Multiple concurrent I/O operations
- High-concurrency endpoints

**Note:** Django ORM is not fully async. Wrap ORM calls with `sync_to_async()`.

## URLs

```python
# apps/blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="article-list"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="article-detail"),
]

# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls")),
]
```

## Forms

```python
from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "status"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 10}),
        }

    def clean_title(self) -> str:
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        return title
```

## Templates

```
templates/
├── base.html
├── includes/
│   ├── _pagination.html
│   └── _messages.html
└── blog/
    ├── article_list.html
    └── article_detail.html
```

Prefix partials with underscore. Use `{% url %}` not hardcoded paths:

```html
{% extends "base.html" %}

{% block content %}
<a href="{% url 'blog:article-detail' slug=article.slug %}">
  {{ article.title }}
</a>
{% endblock %}
```

## Type Hints

Add type hints throughout for mypy / IDE support:

```python
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet


def article_list(request: HttpRequest) -> HttpResponse:
    articles: QuerySet[Article] = Article.objects.filter(status="published")
    return render(request, "blog/article_list.html", {"articles": articles})
```

```bash
# pyproject.toml
[tool.mypy]
plugins = ["mypy_django_plugin.main"]
django_settings_module = "config.settings.dev"

# Run
mypy apps/
```

## Running with ASGI (for async)

```bash
# Install
pip install uvicorn

# Development
uvicorn config.asgi:application --reload

# Production
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -w 4
```

## Testing

```python
import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_article_list_view(client: Client):
    response = client.get(reverse("blog:article-list"))
    assert response.status_code == 200
    assert "articles" in response.context


@pytest.mark.django_db
async def test_async_view():
    """Async test for async views."""
    from django.test import AsyncClient
    client = AsyncClient()
    response = await client.get("/api/weather/?city=Paris")
    assert response.status_code == 200
```

Use `pytest-django` + `factory_boy` for ergonomic testing.

## Common Pitfalls

1. **N+1 queries**: Use `select_related` (FK) and `prefetch_related` (M2M). Check with django-debug-toolbar.

2. **Sync calls in async views**: Wrap ORM with `sync_to_async()`. Use `httpx` not `requests`.

3. **Missing migrations**: Run `makemigrations` after model changes. Commit migrations.

4. **Hardcoded URLs**: Use `{% url %}` in templates, `reverse()` in Python.

5. **No indexes**: Add `db_index=True` or `Meta.indexes` for filtered/ordered fields.

6. **Fat views**: Move business logic to model methods or a service layer.

## Modern Tooling

```bash
# pyproject.toml dev dependencies
django-debug-toolbar    # Query debugging
django-extensions       # shell_plus, show_urls
django-environ          # Environment variables
pytest-django           # Testing
factory-boy             # Test fixtures
mypy + django-stubs     # Type checking
ruff                    # Linting (replaces flake8/isort/black)
```

## Management Commands

Keep commands thin — delegate logic to services.

### Structure

```
apps/blog/
├── management/
│   └── commands/
│       └── publish_scheduled.py
└── services/
    └── publishing.py
```

### Service Layer

```python
# apps/blog/services/publishing.py
from dataclasses import dataclass
from django.utils import timezone
from apps.blog.models import Article


@dataclass
class PublishResult:
    published_count: int
    failed_ids: list[int]


def publish_scheduled_articles(dry_run: bool = False) -> PublishResult:
    """
    Publish all articles scheduled for now or earlier.
    
    Business logic lives here — testable without command scaffolding.
    """
    now = timezone.now()
    articles = Article.objects.filter(
        status=Article.Status.SCHEDULED,
        publish_at__lte=now,
    )
    
    if dry_run:
        return PublishResult(published_count=articles.count(), failed_ids=[])
    
    published = 0
    failed = []
    
    for article in articles:
        try:
            article.status = Article.Status.PUBLISHED
            article.save(update_fields=["status", "updated_at"])
            published += 1
        except Exception:
            failed.append(article.id)
    
    return PublishResult(published_count=published, failed_ids=failed)
```

### Command (Thin Wrapper)

```python
# apps/blog/management/commands/publish_scheduled.py
from django.core.management.base import BaseCommand, CommandError
from apps.blog.services.publishing import publish_scheduled_articles


class Command(BaseCommand):
    help = "Publish articles that are scheduled for now or earlier"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be published without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be made"))
        
        result = publish_scheduled_articles(dry_run=dry_run)
        
        if result.failed_ids:
            self.stderr.write(
                self.style.ERROR(f"Failed to publish: {result.failed_ids}")
            )
        
        self.stdout.write(
            self.style.SUCCESS(f"Published {result.published_count} articles")
        )
```

### Testing

```python
# apps/blog/tests/test_services.py
import pytest
from django.utils import timezone
from apps.blog.services.publishing import publish_scheduled_articles
from apps.blog.models import Article


@pytest.mark.django_db
def test_publish_scheduled_articles(article_factory):
    # Create scheduled article in the past
    article = article_factory(
        status=Article.Status.SCHEDULED,
        publish_at=timezone.now() - timezone.timedelta(hours=1),
    )
    
    result = publish_scheduled_articles()
    
    assert result.published_count == 1
    article.refresh_from_db()
    assert article.status == Article.Status.PUBLISHED


@pytest.mark.django_db
def test_publish_dry_run_no_changes(article_factory):
    article = article_factory(
        status=Article.Status.SCHEDULED,
        publish_at=timezone.now() - timezone.timedelta(hours=1),
    )
    
    result = publish_scheduled_articles(dry_run=True)
    
    assert result.published_count == 1
    article.refresh_from_db()
    assert article.status == Article.Status.SCHEDULED  # Unchanged
```

### Command Guidelines

| Layer | Responsibility |
|-------|----------------|
| **Command** | Parse args, call service, format output, exit codes |
| **Service** | Business logic, DB operations, return typed results |

**Command should NOT:**
- Contain business logic
- Query the database directly (beyond simple lookups)
- Be the only way to run the logic

**Benefits:**
- Services are reusable (views, tasks, other commands)
- Services are testable without management command overhead
- Commands stay focused on CLI concerns

## When to Use Separate Skills

- **django-api**: For REST APIs with Django Ninja or DRF
- **django-admin**: For complex admin customizations