# Fully-Typed Django Models

This example demonstrates best practices for creating fully-typed Django models optimized for AI coding assistants.

## Basic Typed Model

```python
"""Example of a fully-typed Django model."""
from typing import Any
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Article(models.Model):
    """A blog article with full type annotations."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title: models.CharField = models.CharField(
        _("title"),
        max_length=200,
        help_text=_("Article title")
    )
    slug: models.SlugField = models.SlugField(
        _("slug"),
        max_length=200,
        unique=True
    )
    content: models.TextField = models.TextField(
        _("content"),
        help_text=_("Article content in Markdown")
    )
    published: models.BooleanField = models.BooleanField(
        _("published"),
        default=False,
        help_text=_("Whether the article is published")
    )
    published_at: models.DateTimeField = models.DateTimeField(
        _("published at"),
        null=True,
        blank=True
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    # Foreign key with type annotation
    author: models.ForeignKey = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_("author")
    )

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["published", "-published_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to auto-generate slug."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

## Typed Model with ManyToMany

```python
"""Example with ManyToMany relationships."""
from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """A tag for categorizing content."""

    name: models.CharField = models.CharField(
        _("name"),
        max_length=50,
        unique=True
    )
    slug: models.SlugField = models.SlugField(
        _("slug"),
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    """A post with tags."""

    title: models.CharField = models.CharField(max_length=200)
    tags: models.ManyToManyField = models.ManyToManyField(
        Tag,
        related_name='posts',
        blank=True
    )

    def __str__(self) -> str:
        return self.title
```

## Typed Abstract Base Model

```python
"""Example of typed abstract base model."""
from typing import Any
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with timestamps."""

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete."""

    is_deleted: models.BooleanField = models.BooleanField(default=False)
    deleted_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark object as deleted."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class Product(TimeStampedModel, SoftDeleteModel):
    """Example model inheriting from multiple abstract bases."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name: models.CharField = models.CharField(max_length=200)
    price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self) -> str:
        return self.name
```

## Typed Model Manager

```python
"""Example of typed model manager."""
from typing import Any
from django.db import models
from django.db.models import QuerySet


class PublishedManager(models.Manager['Article']):
    """Manager for published articles."""

    def get_queryset(self) -> QuerySet['Article']:
        """Return only published articles."""
        return super().get_queryset().filter(published=True)


class Article(models.Model):
    """Article with typed manager."""

    title: models.CharField = models.CharField(max_length=200)
    published: models.BooleanField = models.BooleanField(default=False)

    # Default manager
    objects: models.Manager['Article'] = models.Manager()

    # Custom manager
    published_objects: PublishedManager = PublishedManager()

    def __str__(self) -> str:
        return self.title
```

## Why Type Annotations Matter

1. **Better IDE Support**: AI coding assistants like GitHub Copilot, Cursor, and Cody understand your code structure better
2. **Fewer Errors**: Type checkers catch bugs before runtime
3. **Self-Documenting**: Type hints serve as inline documentation
4. **Refactoring Safety**: AI tools can suggest safer refactorings when types are known
5. **Team Collaboration**: Makes code intent clearer to other developers

## Benefits for AI Tooling

When you have full type annotations:

- **More Accurate Completions**: AI knows what fields exist and their types
- **Better Import Suggestions**: AI can auto-import the right types
- **Context-Aware Refactoring**: AI understands relationships between models
- **Smarter Error Detection**: AI catches type mismatches as you type
- **Enhanced Documentation**: AI can generate better docstrings

## Running Type Checks

```bash
# Check all files
/usr/bin/make typecheck

# Or directly with mypy
uv run mypy .

# Check specific file
uv run mypy apps/blog/models.py
```

## Common Type Patterns

### Optional Fields

```python
# Field that can be None
description: models.TextField = models.TextField(
    null=True,
    blank=True
)
```

### Custom Methods

```python
def get_absolute_url(self) -> str:
    """Return the URL for this article."""
    from django.urls import reverse
    return reverse('article-detail', kwargs={'slug': self.slug})

def word_count(self) -> int:
    """Count words in content."""
    return len(self.content.split())
```

### Properties

```python
@property
def is_published(self) -> bool:
    """Check if article is published."""
    return self.published and self.published_at is not None
```

## Tips

1. Always annotate model fields with their Django field type
2. Use `-> str` for `__str__` methods
3. Use `-> None` for methods that don't return values
4. Use `Any` sparingly - prefer specific types when possible
5. Add type hints to `save()`, `delete()`, and custom methods
6. Use generics for managers: `models.Manager['ModelName']`
