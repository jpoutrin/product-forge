# Django Remediation Checklist

Detailed steps to fix common parallelization blockers in Django projects.

## App Boundary Issues

### Problem: God App
A single Django app that contains too much functionality.

**Detection:**
- App with >20 model classes
- App imported by >50% of other apps
- Mixed concerns (users + orders + products in one app)

```bash
# Count models per app
for app in apps/*/; do
  count=$(grep -c "class.*models.Model" "$app/models.py" 2>/dev/null || echo 0)
  echo "$app: $count models"
done
```

**Fix:**
1. Map all models and their relationships
2. Group by domain (users, orders, products, etc.)
3. Create new apps for each domain
4. Move models incrementally with migrations:

```bash
# Create new app
python manage.py startapp orders apps/orders

# Move model step by step:
# 1. Create model in new app
# 2. Create migration
# 3. Update all imports
# 4. Create data migration if needed
# 5. Remove old model
```

### Problem: Circular Imports Between Apps
App A imports from App B, and App B imports from App A.

**Detection:**
```bash
# Find cross-app imports
grep -r "from apps\." --include="*.py" apps/ | \
  awk -F: '{print $1 " -> " $2}' | \
  grep -v __pycache__
```

```python
# Programmatic check
import importlib
import sys

sys.setrecursionlimit(50)  # Low limit to catch cycles
try:
    importlib.import_module("apps.users")
except RecursionError:
    print("Circular import detected!")
```

**Fix:**

1. **Extract shared models to `shared/` app:**
```python
# apps/shared/models.py
class BaseModel(models.Model):
    """Shared base model."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

2. **Use string references for ForeignKeys:**
```python
# Instead of importing the model
from apps.users.models import User

class Order(models.Model):
    # Use string reference
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
```

3. **Use dependency injection for services:**
```python
# apps/orders/services.py
from typing import Protocol

class UserServiceProtocol(Protocol):
    def get_by_id(self, user_id: int) -> "User": ...

class OrderService:
    def __init__(self, user_service: UserServiceProtocol):
        self.user_service = user_service
```

### Problem: Cross-App Model Inheritance

**Detection:**
```bash
grep -r "class.*models\." --include="models.py" apps/ | grep -v "models.Model"
```

**Fix:**
1. Use abstract base classes in `shared/`
2. Or use composition instead of inheritance
3. Or duplicate fields (denormalization)

```python
# Prefer abstract base class
# apps/shared/models.py
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# apps/orders/models.py
from apps.shared.models import TimestampedModel

class Order(TimestampedModel):
    # Inherits timestamps without cross-app dependency
    pass
```

## Shared State Issues

### Problem: Global Variables

**Detection:**
```bash
# Find module-level mutable state
grep -rn "^[a-z_]*\s*=\s*\[\|^[a-z_]*\s*=\s*{" --include="*.py" apps/
```

**Fix:**
1. Convert to class attributes or instance variables
2. Use Django's cache framework for shared state
3. Pass state via function arguments

```python
# Before
_cache = {}  # Global mutable state

def get_user(user_id):
    if user_id in _cache:
        return _cache[user_id]
    ...

# After - use Django cache
from django.core.cache import cache

def get_user(user_id: int) -> User:
    cache_key = f"user:{user_id}"
    user = cache.get(cache_key)
    if user is None:
        user = User.objects.get(id=user_id)
        cache.set(cache_key, user, timeout=300)
    return user
```

### Problem: Cross-App Signals

**Detection:**
```bash
# Find signal receivers
grep -rn "@receiver\|\.connect(" --include="*.py" apps/
```

**Fix:**
1. Document all signal side effects
2. Convert to explicit service calls
3. Move signals to app that owns the side effect

```python
# Before - implicit cross-app signal
# apps/orders/signals.py
from django.db.models.signals import post_save
from apps.users.models import User
from apps.orders.models import UserStats

@receiver(post_save, sender=User)
def update_user_stats(sender, instance, created, **kwargs):
    if created:
        UserStats.objects.create(user=instance)

# After - explicit service call
# apps/users/services.py
class UserService:
    def __init__(self, stats_service: "StatsService"):
        self.stats_service = stats_service

    def create_user(self, email: str, name: str) -> User:
        user = User.objects.create(email=email, name=name)
        self.stats_service.initialize_for_user(user.id)
        return user
```

### Problem: Shared File Writes

**Detection:**
```bash
# Find file operations
grep -rn "open(\|\.write(\|Path(" --include="*.py" apps/
```

**Fix:**
1. Designate file ownership per app
2. Use Django's storage backend
3. Use message queue for shared files

```python
# Use Django storage with app-specific paths
from django.core.files.storage import default_storage

def save_order_document(order_id: int, content: bytes) -> str:
    path = f"orders/{order_id}/document.pdf"
    return default_storage.save(path, ContentFile(content))
```

## API Contract Issues

### Problem: Serializers Using `__all__`

**Detection:**
```bash
grep -rn 'fields\s*=\s*"__all__"\|fields\s*=\s*.__all__.' --include="*.py" apps/
```

**Fix:**
Always use explicit field lists:

```python
# Before
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"  # Bad - exposes all fields

# After
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at"]
        read_only_fields = ["id", "created_at"]
```

### Problem: Missing Type Hints

**Detection:**
```bash
# Find functions without return type hints
grep -rn "def .*):$" --include="*.py" apps/ | head -20
```

**Fix:**
1. Enable mypy with django-stubs
2. Add type hints incrementally, starting with public APIs
3. Use strict mode for new code

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
plugins = ["mypy_django_plugin.main", "mypy_drf_plugin.main"]

# Start permissive, tighten gradually
strict = false
disallow_untyped_defs = true
warn_return_any = true

[[tool.mypy.overrides]]
module = "*.migrations.*"
ignore_errors = true
```

```python
# Add type hints to views
from rest_framework.request import Request
from rest_framework.response import Response

def list_users(request: Request) -> Response:
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
```

### Problem: No API Documentation

**Fix:**
Set up drf-spectacular for OpenAPI:

```bash
pip install drf-spectacular
```

```python
# config/settings/base.py
INSTALLED_APPS = [
    ...
    "drf_spectacular",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Project API",
    "VERSION": "1.0.0",
}
```

```python
# config/urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
```

## Test Infrastructure Issues

### Problem: No Test Setup

**Fix:**
1. Add pytest-django
2. Create conftest.py
3. Set up factories

```bash
pip install pytest pytest-django factory-boy
```

```python
# conftest.py
import pytest

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass
```

```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
addopts = "-v --tb=short"
```

### Problem: Tests Share Database State

**Detection:**
- Tests pass individually, fail when run together
- Test order affects results

**Fix:**
1. Use pytest-django's `@pytest.mark.django_db`
2. Use TransactionTestCase for integration tests
3. Create fresh data per test with factories

```python
import pytest
from apps.users.tests.factories import UserFactory

@pytest.mark.django_db
class TestUserService:
    def test_get_user(self) -> None:
        # Each test gets clean database
        user = UserFactory()  # Create fresh data
        service = UserService()

        result = service.get_by_id(user.id)

        assert result.email == user.email

@pytest.mark.django_db(transaction=True)
class TestOrderIntegration:
    """Integration tests that need transaction control."""

    def test_order_creation_rollback(self) -> None:
        # Test transaction behavior
        pass
```

### Problem: Missing Fixtures/Factories

**Fix:**
Set up Factory Boy:

```python
# apps/users/tests/factories.py
import factory
from apps.users.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")
    is_active = True

class AdminUserFactory(UserFactory):
    is_staff = True
    is_superuser = True
```

```python
# apps/orders/tests/factories.py
import factory
from apps.orders.models import Order
from apps.users.tests.factories import UserFactory

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total = factory.Faker("random_int", min=100, max=10000)
    status = "pending"
```

## Documentation Issues

### Problem: No CLAUDE.md

**Fix:**
Create minimal CLAUDE.md:

```markdown
# Project Conventions

## Code Style
- Use ruff for linting and formatting: `ruff check . && ruff format .`
- Use mypy for type checking: `mypy apps/`
- Follow PEP 8 naming conventions

## Architecture
- `apps/users/` - User management and authentication
- `apps/orders/` - Order processing
- `apps/shared/` - Shared utilities and base classes

## Patterns
- Services for business logic (not in views)
- Explicit serializer fields (never `__all__`)
- Type hints on all public functions
- Factory Boy for test data

## Testing
- Use pytest: `pytest`
- Colocate tests: `apps/users/tests/test_services.py`
- One assertion per test when possible

## Commands
```bash
python manage.py runserver     # Start dev server
pytest                         # Run tests
ruff check . --fix            # Lint and fix
mypy apps/                    # Type check
```
```

### Problem: Inconsistent Code Style

**Fix:**
1. Add ruff configuration
2. Run formatter on entire codebase
3. Add pre-commit hook

```bash
pip install ruff pre-commit
```

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP"]

[tool.ruff.isort]
known-first-party = ["apps", "config"]
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

```bash
# One-time format
ruff format .
ruff check . --fix

# Install pre-commit
pre-commit install
```

## Migration Issues

### Problem: Too Many Migrations

**Fix:**
Squash migrations before parallel work:

```bash
# Squash migrations for an app
python manage.py squashmigrations users 0001 0015

# After testing, delete old migrations
rm apps/users/migrations/0002_*.py
rm apps/users/migrations/0003_*.py
# ... etc
```

### Problem: Migration Conflicts

**Fix:**
1. Ensure all migrations are applied before parallel work
2. Use `--merge` during integration only
3. Document migration dependencies in task specs

```bash
# Check for unapplied migrations
python manage.py showmigrations | grep "\[ \]"

# Merge conflicting migrations during integration
python manage.py makemigrations --merge
```

## Verification Commands

After remediation, verify readiness:

```bash
# Check for circular imports
python -c "import apps" 2>&1 | grep -i "circular\|recursion"

# Lint entire codebase
ruff check .

# Type check
mypy apps/

# Run all tests
pytest --tb=short

# Check for __all__ serializers
grep -r 'fields\s*=\s*"__all__"' --include="*.py" apps/

# Verify migrations
python manage.py migrate --check
python manage.py makemigrations --check --dry-run
```
