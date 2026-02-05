# Django Project Setup Skill

Comprehensive skill for setting up production-ready Django 6.0 projects with modern tooling.

## Overview

This skill automates the creation of a Django 6.0 project with:

- **Modern Stack**: uv, direnv, PostgreSQL, HTMX, OAuth, DRF
- **Testing**: pytest-django + factory_boy
- **Type Safety**: mypy + django-stubs
- **Code Quality**: ruff for linting and formatting
- **UUID Models**: All models use UUID primary keys from day 1
- **Docker Compose**: Local PostgreSQL container
- **Production Ready**: Split settings, proper .gitignore, security defaults

## Usage

```bash
/django-project-setup myproject
```

The skill will guide you through:

1. Asking for the first app name (e.g., 'accounts', 'blog', 'api')
2. Creating the complete project structure
3. Setting up all configuration files
4. Installing dependencies
5. Running initial migrations
6. Creating a superuser

## What Gets Created

```
myproject/
├── config/              # Settings and core config
│   ├── settings/
│   │   ├── base.py      # Core settings
│   │   ├── dev.py       # Development
│   │   └── prod.py      # Production
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   └── core/            # Core app with UUIDModel
├── templates/           # Global templates
├── static/              # Global static files
├── docker-compose.yml   # PostgreSQL container
├── Makefile             # Development commands
├── pyproject.toml       # Dependencies and tool config
├── pytest.ini           # Test configuration
├── conftest.py          # Test fixtures
├── .envrc               # Environment config
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── manage.py
└── CLAUDE.md            # Project documentation
```

## After Setup

Start developing immediately:

```bash
# Start database
/usr/bin/make start-docker

# Run migrations
/usr/bin/make migrate

# Create superuser
/usr/bin/make createsuperuser

# Start server
/usr/bin/make runserver

# Run tests
/usr/bin/make test
```

## Features

### UUID Primary Keys

All models automatically use UUID primary keys:

```python
from apps.core.models import UUIDModel

class MyModel(UUIDModel):
    # id, created_at, updated_at automatically added
    name = models.CharField(max_length=100)
```

### HTMX Integration

Views support both full page and HTMX requests:

```python
def my_view(request):
    if request.htmx:
        return render(request, 'partials/content.html')
    return render(request, 'page.html')
```

### Testing Infrastructure

Modern testing with pytest and factories:

```python
@pytest.mark.django_db
def test_my_model(my_model_factory):
    obj = my_model_factory(name="Test")
    assert obj.name == "Test"
```

### API Development

Django REST Framework with OAuth:

```python
class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

### Type Safety

Full mypy support with django-stubs:

```python
from typing import Optional
from django.http import HttpRequest, HttpResponse

def my_view(request: HttpRequest) -> HttpResponse:
    # Type-safe Django code
    pass
```

## Templates

The skill includes templates for:

- `CLAUDE.md` - Project-specific documentation
- `docker-compose.yml` - PostgreSQL container
- `Makefile` - Common development tasks
- `.envrc` - Environment configuration
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules
- `pytest.ini` - Test configuration
- `conftest.py` - Test fixtures

## Examples

The skill includes comprehensive examples for:

- **UUID Models** - Using UUID primary keys throughout
- **HTMX Integration** - Building interactive UIs without JS frameworks
- **Testing** - pytest-django with factory_boy patterns

## Requirements

- Python 3.12+ (Django 6.0 requirement)
- uv (will be installed if missing)
- direnv (recommended)
- Docker (for local PostgreSQL)

## Related Skills

- `/python-experts:django-dev` - Django development patterns
- `/python-experts:django-api` - API development with DRF
- `/devops-data:direnv` - Environment management

## Implementation Notes

The skill follows these principles:

1. **Modern Python**: Uses Python 3.12+ features
2. **Type Safety**: Full type hints throughout
3. **Testing First**: Testing infrastructure set up from day 1
4. **Security**: Follows Django security best practices
5. **Scalability**: Split settings for different environments
6. **Developer Experience**: Make commands for common tasks
7. **Documentation**: Comprehensive CLAUDE.md for the project

## Version Compatibility

- Django: 6.0+
- Python: 3.12+
- PostgreSQL: 16+
- uv: Latest
- pytest: 8+
- mypy: 1.8+
- ruff: 0.1+

## Support

For issues or questions:

1. Check the generated `CLAUDE.md` in your project
2. Review the example files in this directory
3. Consult the Django 6.0 documentation
4. Use `/python-experts:django-dev` for development questions
