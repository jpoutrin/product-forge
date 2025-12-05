---
name: python-style
description: Automatic enforcement of Python coding style, PEP standards, type hints, and modern Python patterns. Use when writing Python code to ensure consistency with PEP 8, proper type hints, Google-style docstrings, and modern Python 3.11+ idioms.
---

# Python Style Best Practices Skill

This skill automatically activates when writing Python code to ensure consistency with PEP standards, type hints, and modern Python idioms.

## Core Standards

- **PEP 8**: Naming conventions, imports, line length
- **Type Hints**: Modern syntax (`list[str]` not `List[str]`, `X | None` not `Optional[X]`)
- **Docstrings**: Google style with Args, Returns, Raises sections
- **Imports**: stdlib → third-party → local, alphabetically sorted

## Naming Conventions

```python
# Classes: PascalCase
class UserAccount:
    pass

# Functions/variables: snake_case
def calculate_total():
    user_name = "john"

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private: single underscore prefix
def _internal_helper():
    pass
```

## Type Hints (Python 3.10+)

```python
# Use built-in generics
def process(items: list[str]) -> dict[str, int]:
    pass

# Use | for Optional/Union
def find_user(id: str) -> User | None:
    pass

# TypedDict for structured dicts
class UserData(TypedDict):
    id: str
    name: str
```

## Function Length Guidelines

- **< 30 lines**: Ideal
- **30-50 lines**: Review for refactoring
- **> 50 lines**: Must be broken down

## Anti-Patterns to Avoid

- Missing type hints
- Bare `except:` clauses
- Magic numbers/strings without constants
- Non-expressive variable names (`d`, `temp`, `x`)
- Vague function names (`process`, `handle`, `do_stuff`)
