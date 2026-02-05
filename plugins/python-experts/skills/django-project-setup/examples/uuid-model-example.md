# UUID Model Example

All models in this Django project use UUID primary keys instead of auto-incrementing integers.

## Base Model

The `UUIDModel` base class is defined in `apps/core/models.py`:

```python
import uuid
from django.db import models


class UUIDModel(models.Model):
    """Abstract base class for models with UUID primary keys."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

## Custom User Model

The custom User model extends both `AbstractUser` and `UUIDModel`:

```python
from django.contrib.auth.models import AbstractUser
from apps.core.models import UUIDModel


class User(AbstractUser, UUIDModel):
    """Custom user model with UUID primary key."""

    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email
```

## Example App Model

When creating new models, inherit from `UUIDModel`:

```python
from django.db import models
from apps.core.models import UUIDModel


class Post(UUIDModel):
    """Blog post with UUID primary key."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    published = models.BooleanField(default=False)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title
```

## Benefits of UUID Primary Keys

1. **Global Uniqueness**: UUIDs are globally unique, not just within a table
2. **Security**: UUIDs don't expose record counts or sequential information
3. **Distributed Systems**: UUIDs can be generated anywhere without coordination
4. **API Design**: UUIDs in URLs don't leak business information
5. **Data Migration**: Merging databases is easier with UUIDs

## Foreign Key Relationships

Foreign keys automatically use UUID type when referencing UUID models:

```python
class Comment(UUIDModel):
    """Comment with UUID primary key and foreign key to Post."""

    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
```

## Querying with UUIDs

```python
import uuid

# Get by UUID
post_uuid = uuid.UUID('550e8400-e29b-41d4-a716-446655440000')
post = Post.objects.get(id=post_uuid)

# Or from string
post = Post.objects.get(id='550e8400-e29b-41d4-a716-446655440000')

# Filter by related UUID
comments = Comment.objects.filter(post_id=post_uuid)
```

## Testing with UUIDs

Factory Boy handles UUID generation automatically:

```python
import factory
from factory.django import DjangoModelFactory
from apps.blog.models import Post


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker('sentence')
    slug = factory.Faker('slug')
    content = factory.Faker('paragraph', nb_sentences=10)
    author = factory.SubFactory('apps.core.factories.UserFactory')
    published = True
```

Test example:

```python
import pytest


@pytest.mark.django_db
class TestPost:
    def test_post_creation(self, post_factory):
        """Test creating a post with UUID."""
        post = post_factory(title="Test Post")
        assert post.id is not None
        assert isinstance(post.id, uuid.UUID)
        assert post.title == "Test Post"
```

## API Serialization

Django REST Framework handles UUIDs automatically:

```python
from rest_framework import serializers
from apps.blog.models import Post


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model."""

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'author', 'published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
```

JSON response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Example Post",
  "slug": "example-post",
  "content": "...",
  "author": "123e4567-e89b-12d3-a456-426614174000",
  "published": true,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

## Admin Configuration

UUIDs work seamlessly with Django Admin:

```python
from django.contrib import admin
from apps.blog.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published', 'created_at']
    list_filter = ['published', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
```

## Database Indexes

PostgreSQL handles UUID indexing efficiently:

```python
class Post(UUIDModel):
    # ...

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author', '-created_at']),  # Composite index
        ]
```
