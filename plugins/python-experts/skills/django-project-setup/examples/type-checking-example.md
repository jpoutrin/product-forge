# Type Checking Example

This example shows how strict type checking works in the generated Django projects.

## mypy Configuration

The generated projects use strict mypy configuration:

```toml
[tool.mypy]
plugins = ["mypy_django_plugin.main"]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true  # ← Strict mode enabled
warn_redundant_casts = true
warn_unused_ignores = true
strict_equality = true
check_untyped_defs = true
```

## What This Means

With `disallow_untyped_defs = true`, mypy will error on ANY function/method without type annotations.

### Examples That Pass

```python
# ✅ Function with return type
def get_user_email(user_id: int) -> str:
    user = User.objects.get(id=user_id)
    return user.email

# ✅ Function with no return value
def send_notification(user: User, message: str) -> None:
    print(f"Sending to {user.email}: {message}")

# ✅ Method with typed parameters
class UserService:
    def create_user(self, email: str, username: str) -> User:
        return User.objects.create(email=email, username=username)

# ✅ Property with return type
class Article(models.Model):
    @property
    def word_count(self) -> int:
        return len(self.content.split())
```

### Examples That Fail

```python
# ❌ No return type annotation
def get_user_email(user_id: int):
    user = User.objects.get(id=user_id)
    return user.email
# mypy error: Function is missing a return type annotation

# ❌ No parameter type annotations
def send_notification(user, message):
    print(f"Sending to {user.email}: {message}")
# mypy error: Function is missing a type annotation for one or more arguments

# ❌ Missing self parameter type in some contexts
def create_user(email, username):
    return User.objects.create(email=email, username=username)
# mypy error: Function is missing a type annotation for one or more arguments
```

## Running Type Checks

```bash
# Check all files
/usr/bin/make typecheck

# Or run mypy directly
uv run mypy .

# Check specific file
uv run mypy apps/blog/models.py

# Show detailed error messages
uv run mypy --show-error-codes .
```

## Common Type Patterns

### Django QuerySets

```python
from django.db.models import QuerySet

def get_active_users() -> QuerySet[User]:
    """Return all active users."""
    return User.objects.filter(is_active=True)
```

### Optional Values

```python
from typing import Optional

def find_user_by_email(email: str) -> Optional[User]:
    """Find user by email, return None if not found."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
```

### Lists and Dictionaries

```python
def get_user_emails(user_ids: list[int]) -> list[str]:
    """Get emails for given user IDs."""
    users = User.objects.filter(id__in=user_ids)
    return [user.email for user in users]

def get_user_data(user: User) -> dict[str, Any]:
    """Convert user to dictionary."""
    return {
        'id': str(user.id),
        'email': user.email,
        'username': user.username,
    }
```

### Generic Types

```python
from typing import Any, Generic, TypeVar

T = TypeVar('T', bound=models.Model)

class Repository(Generic[T]):
    """Generic repository pattern."""

    def __init__(self, model: type[T]) -> None:
        self.model = model

    def get_by_id(self, obj_id: Any) -> T:
        return self.model.objects.get(id=obj_id)

    def get_all(self) -> QuerySet[T]:
        return self.model.objects.all()
```

### View Type Annotations

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def my_view(request: HttpRequest) -> HttpResponse:
    """Example view with proper types."""
    context = {'message': 'Hello, world!'}
    return render(request, 'template.html', context)
```

### API View Type Annotations (DRF)

```python
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET', 'POST'])
def user_list(request: Request) -> Response:
    """List or create users."""
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
```

## Benefits

1. **Catch Bugs Early**: Type errors are caught at development time, not runtime
2. **Better Refactoring**: AI tools can suggest safe refactorings
3. **Self-Documenting**: Function signatures document expected types
4. **IDE Support**: Better autocomplete and inline documentation
5. **Team Collaboration**: Makes code intent crystal clear

## Gradual Typing

If you need to work with untyped third-party code, you can use `# type: ignore`:

```python
# Suppress type checking for a specific line
result = untyped_library.get_data()  # type: ignore[attr-defined]

# Or for a whole function (not recommended)
def legacy_function() -> None:  # type: ignore
    # Old code without types
    pass
```

## CI/CD Integration

Add type checking to your CI pipeline:

```yaml
# .github/workflows/ci.yml
- name: Run type checks
  run: uv run mypy .
```

This ensures all code committed to the repository passes strict type checking.
