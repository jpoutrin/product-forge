# Django Infrastructure Setup

Scripts and templates to set up parallelization infrastructure for Django projects.

## Directory Structure Setup

```bash
#!/bin/bash
# setup-parallel-infra.sh

# Create orchestration directory
mkdir -p .claude/{tasks,contracts}

# Create readiness report placeholder
cat > .claude/readiness-report.md << 'EOF'
# Django Parallelization Readiness Report

> Run assessment to populate this report.

## Overall Score: Not Yet Assessed
EOF

# Create architecture template
cat > .claude/architecture.md << 'EOF'
# Django System Architecture

## Overview
[High-level system description]

## Django Apps
| App | Responsibility | Dependencies |
|-----|----------------|--------------|
| users | User management, auth | - |
| orders | Order processing | users |
| products | Product catalog | - |

## Data Flow
[How data moves through the system]

## App Boundaries
[Where parallel work can happen safely]

## External Dependencies
[Databases, caches, external APIs, task queues]
EOF

echo "Created .claude/ structure"
```

## CLAUDE.md Template for Django

```markdown
# Django Project Conventions

## Overview
[Brief project description]

## Project Structure
```
project/
├── config/           # Django settings module
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/             # Django applications
│   ├── users/
│   ├── orders/
│   └── shared/       # Shared utilities only
├── tests/            # Integration tests
├── scripts/          # Management scripts
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

## Code Style

### General
- Python 3.11+ required
- Type hints on all public functions
- Maximum file length: 300 lines
- Maximum function length: 50 lines

### Naming
- Files: snake_case (`user_service.py`)
- Classes: PascalCase (`UserService`)
- Functions/variables: snake_case (`get_user_by_id`)
- Constants: SCREAMING_SNAKE (`MAX_RETRY_COUNT`)

### Imports
```python
# Standard library
import os
from datetime import datetime

# Third-party
from django.db import models
from rest_framework import serializers

# Local apps
from apps.users.models import User
from apps.shared.utils import generate_id
```

## Django Patterns

### Models
```python
from django.db import models

class User(models.Model):
    """User account model.

    Attributes:
        email: Unique email address.
        name: Display name.
        created_at: Account creation timestamp.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email
```

### Serializers
```python
from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model.

    Always use explicit fields, never __all__.
    """
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at"]
        read_only_fields = ["id", "created_at"]
```

### Views
```python
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.models import User
from apps.users.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """API endpoints for user management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request: Request) -> Response:
        """List all users with pagination."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

### Services
```python
from dataclasses import dataclass
from apps.users.models import User
from apps.shared.exceptions import NotFoundError

@dataclass
class UserService:
    """Business logic for user operations."""

    def get_by_id(self, user_id: int) -> User:
        """Get user by ID or raise NotFoundError."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFoundError(f"User {user_id} not found")

    def create(self, email: str, name: str) -> User:
        """Create new user."""
        return User.objects.create(email=email, name=name)
```

## Error Handling

```python
# apps/shared/exceptions.py
class AppError(Exception):
    """Base application error."""
    status_code = 500

class NotFoundError(AppError):
    """Resource not found."""
    status_code = 404

class ValidationError(AppError):
    """Validation failed."""
    status_code = 400
```

```python
# Exception handler for DRF
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    if isinstance(exc, AppError):
        return Response(
            {"error": str(exc), "code": exc.__class__.__name__},
            status=exc.status_code
        )
    return exception_handler(exc, context)
```

## Logging

```python
import structlog

logger = structlog.get_logger(__name__)

# Structured logging
logger.info("user_created", user_id=user.id, email=user.email)
logger.error("process_failed", error=str(exc), context={"order_id": order_id})
```

## Testing

### Test Structure
```
apps/
├── users/
│   ├── models.py
│   ├── views.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       └── factories.py
```

### Test Conventions
```python
import pytest
from apps.users.tests.factories import UserFactory

@pytest.mark.django_db
class TestUserService:
    """Tests for UserService."""

    def test_get_by_id_returns_user_when_found(self) -> None:
        """Should return user when ID exists."""
        user = UserFactory()
        service = UserService()

        result = service.get_by_id(user.id)

        assert result.id == user.id

    def test_get_by_id_raises_not_found_when_missing(self) -> None:
        """Should raise NotFoundError when user doesn't exist."""
        service = UserService()

        with pytest.raises(NotFoundError):
            service.get_by_id(99999)
```

### Factories
```python
import factory
from apps.users.models import User

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")
```

## Git Conventions

- Branch: `feature/task-name`, `fix/bug-name`
- Commits: conventional commits (`feat:`, `fix:`, `docs:`)
- PR: require review before merge

## Commands

```bash
# Development
python manage.py runserver              # Start dev server
python manage.py shell_plus             # Enhanced shell

# Database
python manage.py migrate                # Apply migrations
python manage.py makemigrations app     # Create migrations

# Testing
pytest                                  # Run all tests
pytest apps/users/                      # Run app tests
pytest --cov=apps --cov-report=html     # Coverage report

# Code Quality
ruff check .                            # Lint code
ruff format .                           # Format code
mypy apps/                              # Type check
```
```

## Contract Templates

### Pydantic/Dataclass Contracts

```python
# .claude/contracts/types.py
"""
Shared domain types for all apps.

IMPORTANT: Changes here affect ALL parallel tasks.
Coordinate before modifying.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypedDict

# === Entities ===

@dataclass(frozen=True)
class UserDTO:
    """User data transfer object."""
    id: int
    email: str
    name: str
    created_at: datetime

@dataclass(frozen=True)
class ProductDTO:
    """Product data transfer object."""
    id: int
    name: str
    price: int  # cents
    status: "ProductStatus"

# === Enums ===

class ProductStatus(str, Enum):
    """Product lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

# === API Types ===

class PaginationMeta(TypedDict):
    """Pagination metadata."""
    page: int
    total: int
    per_page: int

class ApiResponse(TypedDict):
    """Standard API response wrapper."""
    data: dict | list
    meta: PaginationMeta | None

class ApiError(TypedDict):
    """Standard API error format."""
    code: str
    message: str
    details: dict | None
```

### OpenAPI Contract Template

```yaml
# .claude/contracts/api-schema.yaml

openapi: 3.0.3
info:
  title: Django Project API
  version: 1.0.0

paths:
  /api/users/:
    get:
      summary: List users
      operationId: listUsers
      tags: [users]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'

  /api/users/{id}/:
    get:
      summary: Get user by ID
      operationId: getUser
      tags: [users]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: Not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ApiError'

components:
  schemas:
    User:
      type: object
      required: [id, email, name, created_at]
      properties:
        id:
          type: integer
        email:
          type: string
          format: email
        name:
          type: string
        created_at:
          type: string
          format: date-time

    UserListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        meta:
          $ref: '#/components/schemas/PaginationMeta'

    PaginationMeta:
      type: object
      properties:
        page:
          type: integer
        total:
          type: integer
        per_page:
          type: integer

    ApiError:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object
```

## pyproject.toml Template

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11"

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
]
ignore = ["E501"]  # line too long (handled by formatter)

[tool.ruff.isort]
known-first-party = ["apps", "config"]

[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["mypy_django_plugin.main", "mypy_drf_plugin.main"]

[[tool.mypy.overrides]]
module = "*.migrations.*"
ignore_errors = true

[tool.django-stubs]
django_settings_module = "config.settings.local"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py", "*_test.py"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["apps"]
omit = ["*/migrations/*", "*/tests/*"]
```

## Verification Script

```bash
#!/bin/bash
# verify-ready.sh

echo "=== Django Parallelization Readiness Check ==="

# Check .claude directory
if [ -d ".claude" ]; then
  echo "✅ .claude/ directory exists"
else
  echo "❌ .claude/ directory missing"
fi

# Check CLAUDE.md
if [ -f "CLAUDE.md" ]; then
  echo "✅ CLAUDE.md exists"
else
  echo "❌ CLAUDE.md missing"
fi

# Check contracts
if [ -d ".claude/contracts" ]; then
  count=$(ls -1 .claude/contracts/ 2>/dev/null | wc -l)
  echo "✅ Contracts directory exists ($count files)"
else
  echo "❌ Contracts directory missing"
fi

# Check for circular imports
echo "Checking for circular imports..."
python -c "
import sys
sys.setrecursionlimit(100)
try:
    import apps
    print('✅ No obvious circular imports')
except RecursionError:
    print('❌ Circular import detected')
except ImportError as e:
    print(f'⚠️  Import error: {e}')
" 2>/dev/null || echo "⚠️  Could not check imports"

# Check for ruff/linting config
if [ -f "pyproject.toml" ] && grep -q "\[tool.ruff\]" pyproject.toml; then
  echo "✅ Ruff configured"
elif [ -f ".ruff.toml" ]; then
  echo "✅ Ruff configured"
else
  echo "⚠️  No Ruff config found"
fi

# Check for mypy config
if [ -f "pyproject.toml" ] && grep -q "\[tool.mypy\]" pyproject.toml; then
  echo "✅ Mypy configured"
elif [ -f "mypy.ini" ]; then
  echo "✅ Mypy configured"
else
  echo "⚠️  No Mypy config found"
fi

# Check for tests
test_count=$(find . -name "test_*.py" -o -name "*_test.py" 2>/dev/null | grep -v __pycache__ | wc -l)
if [ "$test_count" -gt 0 ]; then
  echo "✅ Test files found ($test_count files)"
else
  echo "⚠️  No test files found"
fi

# Check for factories
if grep -r "factory.Factory\|DjangoModelFactory" --include="*.py" . >/dev/null 2>&1; then
  echo "✅ Factory Boy factories found"
else
  echo "⚠️  No factories found (recommended for testing)"
fi

# Check for serializers with __all__
bad_serializers=$(grep -r 'fields\s*=\s*"__all__"\|fields\s*=\s*.__all__.' --include="*.py" . 2>/dev/null | grep -v __pycache__ | wc -l)
if [ "$bad_serializers" -eq 0 ]; then
  echo "✅ No serializers using __all__"
else
  echo "⚠️  Found $bad_serializers serializers using __all__ (should use explicit fields)"
fi

# Check migration count per app
echo ""
echo "=== Migration Analysis ==="
find . -path "*/migrations/*.py" -not -name "__init__.py" 2>/dev/null | \
  grep -v __pycache__ | \
  sed 's|.*/\([^/]*\)/migrations/.*|\1|' | \
  sort | uniq -c | sort -rn | head -10

echo ""
echo "=== Assessment Complete ==="
```
