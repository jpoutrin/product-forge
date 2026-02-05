# Testing Examples

This project uses pytest-django and factory_boy for modern testing.

## Test Structure

```
apps/
└── blog/
    ├── models.py
    ├── views.py
    ├── factories.py          # Factory Boy factories
    └── tests/
        ├── __init__.py
        ├── test_models.py     # Model tests
        ├── test_views.py      # View tests
        ├── test_api.py        # API tests
        └── test_integration.py # Integration tests
```

## Factory Boy Factories

**apps/blog/factories.py**:

```python
import factory
from factory.django import DjangoModelFactory
from apps.blog.models import Post, Comment
from apps.core.factories import UserFactory


class PostFactory(DjangoModelFactory):
    """Factory for Post model."""

    class Meta:
        model = Post

    title = factory.Faker('sentence', nb_words=6)
    slug = factory.Faker('slug')
    content = factory.Faker('paragraph', nb_sentences=10)
    author = factory.SubFactory(UserFactory)
    published = True

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags after creation."""
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class CommentFactory(DjangoModelFactory):
    """Factory for Comment model."""

    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker('paragraph', nb_sentences=3)
```

**Register factories in conftest.py**:

```python
from pytest_factoryboy import register
from apps.blog.factories import PostFactory, CommentFactory

register(PostFactory)
register(CommentFactory)
```

## Model Tests

**apps/blog/tests/test_models.py**:

```python
import pytest
from django.db import IntegrityError
from apps.blog.models import Post


@pytest.mark.django_db
class TestPostModel:
    """Tests for Post model."""

    def test_post_creation(self, post_factory):
        """Test creating a post."""
        post = post_factory(title="Test Post")
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.author is not None

    def test_post_str(self, post_factory):
        """Test post string representation."""
        post = post_factory(title="My Title")
        assert str(post) == "My Title"

    def test_slug_unique(self, post_factory):
        """Test slug must be unique."""
        post_factory(slug="test-slug")
        with pytest.raises(IntegrityError):
            post_factory(slug="test-slug")

    def test_post_ordering(self, post_factory):
        """Test posts are ordered by created_at desc."""
        post1 = post_factory()
        post2 = post_factory()
        posts = Post.objects.all()
        assert posts[0] == post2  # Most recent first
        assert posts[1] == post1

    def test_unpublished_not_in_published(self, post_factory):
        """Test unpublished posts filtered correctly."""
        post_factory(published=True)
        post_factory(published=False)
        assert Post.objects.filter(published=True).count() == 1


@pytest.mark.django_db
class TestCommentModel:
    """Tests for Comment model."""

    def test_comment_creation(self, comment_factory):
        """Test creating a comment."""
        comment = comment_factory()
        assert comment.id is not None
        assert comment.post is not None
        assert comment.author is not None

    def test_comment_cascade_delete(self, post_factory, comment_factory):
        """Test comments deleted when post deleted."""
        post = post_factory()
        comment_factory(post=post)
        comment_factory(post=post)
        assert post.comments.count() == 2

        post.delete()
        # Comments should be deleted (CASCADE)
```

## View Tests

**apps/blog/tests/test_views.py**:

```python
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestPostListView:
    """Tests for post list view."""

    def test_post_list_status(self, client):
        """Test post list returns 200."""
        url = reverse('blog:post_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_post_list_shows_published(self, client, post_factory):
        """Test only published posts shown."""
        published = post_factory(published=True, title="Published")
        unpublished = post_factory(published=False, title="Draft")

        url = reverse('blog:post_list')
        response = client.get(url)

        assert published.title.encode() in response.content
        assert unpublished.title.encode() not in response.content

    def test_post_list_htmx(self, client):
        """Test HTMX partial response."""
        url = reverse('blog:post_list')
        response = client.get(url, HTTP_HX_REQUEST='true')

        assert response.status_code == 200
        assert b'<!DOCTYPE html>' not in response.content


@pytest.mark.django_db
class TestPostDetailView:
    """Tests for post detail view."""

    def test_post_detail_status(self, client, post_factory):
        """Test post detail returns 200."""
        post = post_factory(published=True)
        url = reverse('blog:post_detail', args=[post.slug])
        response = client.get(url)
        assert response.status_code == 200

    def test_unpublished_post_404(self, client, post_factory):
        """Test unpublished post returns 404."""
        post = post_factory(published=False)
        url = reverse('blog:post_detail', args=[post.slug])
        response = client.get(url)
        assert response.status_code == 404

    def test_post_shows_comments(self, client, post_factory, comment_factory):
        """Test post shows its comments."""
        post = post_factory(published=True)
        comment = comment_factory(post=post, content="Test comment")

        url = reverse('blog:post_detail', args=[post.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert b'Test comment' in response.content


@pytest.mark.django_db
class TestAddCommentView:
    """Tests for add comment view."""

    def test_add_comment_requires_auth(self, client, post_factory):
        """Test adding comment requires authentication."""
        post = post_factory(published=True)
        url = reverse('blog:add_comment', args=[post.slug])
        response = client.post(url, {'content': 'Test'})
        assert response.status_code == 302  # Redirect to login

    def test_add_comment_success(self, authenticated_client, post_factory):
        """Test authenticated user can add comment."""
        post = post_factory(published=True)
        url = reverse('blog:add_comment', args=[post.slug])
        response = authenticated_client.post(
            url,
            {'content': 'Test comment'},
            HTTP_HX_REQUEST='true'
        )
        assert response.status_code == 200
        assert post.comments.count() == 1

    def test_add_comment_empty_fails(self, authenticated_client, post_factory):
        """Test empty comment fails."""
        post = post_factory(published=True)
        url = reverse('blog:add_comment', args=[post.slug])
        response = authenticated_client.post(
            url,
            {'content': ''},
            HTTP_HX_REQUEST='true'
        )
        assert response.status_code == 400
```

## API Tests

**apps/blog/tests/test_api.py**:

```python
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPostAPI:
    """Tests for Post API."""

    def test_list_posts_requires_auth(self, api_client):
        """Test listing posts requires authentication."""
        url = reverse('api:post-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_posts_success(self, authenticated_client, post_factory):
        """Test authenticated user can list posts."""
        post_factory.create_batch(3, published=True)

        url = reverse('api:post-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_retrieve_post(self, authenticated_client, post_factory):
        """Test retrieving single post."""
        post = post_factory(published=True)
        url = reverse('api:post-detail', args=[post.id])
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(post.id)
        assert response.data['title'] == post.title

    def test_create_post(self, authenticated_client, user):
        """Test creating post via API."""
        url = reverse('api:post-list')
        data = {
            'title': 'New Post',
            'slug': 'new-post',
            'content': 'Test content',
            'published': True
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Post'
        assert response.data['author'] == str(user.id)

    def test_update_post(self, authenticated_client, post_factory, user):
        """Test updating post via API."""
        post = post_factory(author=user)
        url = reverse('api:post-detail', args=[post.id])
        data = {'title': 'Updated Title'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

    def test_delete_post(self, authenticated_client, post_factory, user):
        """Test deleting post via API."""
        post = post_factory(author=user)
        url = reverse('api:post-detail', args=[post.id])
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestPostAPIPermissions:
    """Tests for Post API permissions."""

    def test_cannot_update_others_post(self, authenticated_client, post_factory):
        """Test user cannot update another user's post."""
        post = post_factory()  # Different author
        url = reverse('api:post-detail', args=[post.id])
        data = {'title': 'Hacked'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_delete_others_post(self, authenticated_client, post_factory):
        """Test user cannot delete another user's post."""
        post = post_factory()  # Different author
        url = reverse('api:post-detail', args=[post.id])
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
```

## Integration Tests

**apps/blog/tests/test_integration.py**:

```python
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestBlogWorkflow:
    """Integration tests for blog workflow."""

    def test_complete_post_lifecycle(self, authenticated_client, user):
        """Test creating, viewing, commenting on, and deleting a post."""
        # Create post via API
        url = reverse('api:post-list')
        post_data = {
            'title': 'Integration Test',
            'slug': 'integration-test',
            'content': 'Test content',
            'published': True
        }
        response = authenticated_client.post(url, post_data)
        assert response.status_code == 201
        post_id = response.data['id']

        # View post detail
        url = reverse('blog:post_detail', args=['integration-test'])
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert b'Integration Test' in response.content

        # Add comment
        url = reverse('blog:add_comment', args=['integration-test'])
        response = authenticated_client.post(
            url,
            {'content': 'Great post!'},
            HTTP_HX_REQUEST='true'
        )
        assert response.status_code == 200

        # Delete post
        url = reverse('api:post-detail', args=[post_id])
        response = authenticated_client.delete(url)
        assert response.status_code == 204

        # Verify post deleted
        url = reverse('blog:post_detail', args=['integration-test'])
        response = authenticated_client.get(url)
        assert response.status_code == 404
```

## Pytest Configuration

**pytest.ini**:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db --cov=apps --cov-report=html --cov-report=term
testpaths = apps
```

## Custom Fixtures

**conftest.py**:

```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def staff_client(api_client, user_factory):
    """Staff user API client."""
    staff_user = user_factory(is_staff=True)
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture
def superuser_client(api_client, user_factory):
    """Superuser API client."""
    superuser = user_factory(is_superuser=True, is_staff=True)
    api_client.force_authenticate(user=superuser)
    return api_client
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest apps/blog/tests/test_models.py

# Run specific test class
uv run pytest apps/blog/tests/test_models.py::TestPostModel

# Run specific test
uv run pytest apps/blog/tests/test_models.py::TestPostModel::test_post_creation

# Run with verbose output
uv run pytest -vv

# Run with coverage report
uv run pytest --cov-report=html

# Run and show print statements
uv run pytest -s

# Run only failed tests from last run
uv run pytest --lf

# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto
```

## Best Practices

1. **Use factories**: Never create objects manually in tests
2. **Test one thing**: Each test should verify one behavior
3. **Clear names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Use fixtures**: Share common setup code
6. **Mark database tests**: Use `@pytest.mark.django_db`
7. **Test edge cases**: Don't just test happy path
8. **Mock external services**: Don't hit real APIs in tests
