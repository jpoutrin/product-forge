# forge-hooks

Hook scripts and validators for Product Forge plugins.

## Overview

`forge-hooks` is a Python package that provides validation utilities for Claude Code hooks in Product Forge plugins. It consolidates common validation logic into a reusable, testable library with both CLI and programmatic interfaces.

## Installation

### From Source (Development)

#### Using `uv` (Recommended)

```bash
# Install in editable mode with dev dependencies
cd /path/to/product-forge
uv sync --all-extras
```

#### Using `pip`

```bash
# Install in editable mode with dev dependencies
cd /path/to/product-forge
pip install -e ".[dev]"
```

### From PyPI (Future)

#### Using `uv`

```bash
uv add forge-hooks
```

#### Using `pip`

```bash
pip install forge-hooks
```

## Features

- **File Discovery**: Find recent and new files using git status and modification times
- **Validation Commands**: Extensible validator framework with built-in validators:
  - `new-file`: Verify a new file was created
  - `contains`: Check file contains required content
  - `ownership`: Validate file ownership rules in task plans
- **Hook I/O**: Standard JSON input/output for Claude Code hooks
- **CLI Interface**: Self-documenting commands via `forge-hooks` CLI
- **Python 3.9+**: Compatible with Python 3.9 and later

## Usage

### CLI Interface

```bash
# Validate a new file was created
forge-hooks validate new-file --directory specs --extension .md

# Validate file contains required sections
forge-hooks validate contains \
  --directory specs \
  --extension .md \
  --contains "## Objective" \
  --contains "## Task Description"

# Validate file ownership rules
forge-hooks validate ownership --directory specs --extension .md
```

### Programmatic Interface

```python
from forge_hooks.validators import NewFileValidator, FileContainsValidator

# Create and run validator
validator = NewFileValidator("specs", ".md", max_age_minutes=5)
result = validator.validate()

if result.is_success:
    print(f"Success: {result.message}")
else:
    print(f"Failed: {result.reason}")
```

### Hook Integration

In your SKILL.md or agent frontmatter:

```yaml
hooks:
  Stop:
    - type: command
      command: forge-hooks validate ownership --directory specs --extension .md
```

## Validators

### new-file

Validates that a new file was created in the specified directory.

**Options:**
- `-d, --directory`: Directory to check (default: `specs`)
- `-e, --extension`: File extension to match (default: `.md`)
- `--max-age`: Maximum file age in minutes (default: `5`)

**Checks:**
1. Git status for untracked/new files
2. File modification time within max age

### contains

Validates that a file contains required content strings (case-sensitive).

**Options:**
- `-d, --directory`: Directory to check (default: `specs`)
- `-e, --extension`: File extension to match (default: `.md`)
- `--contains`: Required string (can be used multiple times)
- `--max-age`: Maximum file age in minutes (default: `5`)

**Checks:**
1. Finds newest file matching pattern
2. Verifies all required strings are present

### ownership

Validates file ownership rules in task orchestration plans.

**Options:**
- `-d, --directory`: Directory to check (default: `specs`)
- `-e, --extension`: File extension to match (default: `.md`)
- `--max-age`: Maximum file age in minutes (default: `5`)

**Validates Four Rules:**
1. Each file is CREATEd by at most one task
2. Parallel tasks (same wave) with unscoped MODIFY target different files
3. Parallel tasks with scoped MODIFY have non-overlapping scopes
4. No task modifies files in its BOUNDARY list

## Development

### Setup

#### Using `uv` (Recommended)

```bash
# Clone and install
git clone <repo-url>
cd product-forge
uv sync --all-extras
```

#### Using `pip`

```bash
# Clone and install
git clone <repo-url>
cd product-forge
pip install -e ".[dev]"
```

### Running Tests

#### Using `uv` (Recommended)

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/validators/test_ownership.py

# Run with verbose output
uv run pytest -v

# Check coverage
uv run pytest --cov=forge_hooks --cov-report=html
```

#### Using `pip`

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/validators/test_ownership.py

# Run with verbose output
pytest -v

# Check coverage
pytest --cov=forge_hooks --cov-report=html
```

### Project Structure

```
src/forge_hooks/
├── __init__.py
├── cli.py              # CLI entry point
├── common/
│   ├── __init__.py
│   ├── hook_io.py      # HookResult, I/O utilities
│   ├── file_discovery.py  # File finding logic
│   └── git_utils.py    # Git operations
└── validators/
    ├── __init__.py
    ├── base.py         # BaseValidator class
    ├── ownership.py    # File ownership validation
    ├── contains.py     # Content validation
    └── new_file.py     # New file validation

tests/
├── conftest.py         # Shared fixtures
├── common/
│   ├── test_hook_io.py
│   └── test_file_discovery.py
└── validators/
    ├── test_new_file.py
    ├── test_contains.py
    └── test_ownership.py
```

## Architecture

### Common Utilities

- **HookResult**: Dataclass for standardized hook results with `ok`, `result`, `message`, `reason` fields
- **File Discovery**: Git-aware file finding with modification time filtering
- **Git Utils**: Subprocess wrappers for git commands

### Validator Pattern

All validators inherit from `BaseValidator`:

```python
class BaseValidator(ABC):
    def __init__(self, directory, extension, max_age_minutes=5):
        ...

    @abstractmethod
    def validate(self) -> HookResult:
        """Override to implement validation logic."""
        pass

    def run(self) -> int:
        """Execute validator with error handling."""
        ...
```

### Building and Publishing

#### Using `uv` (Recommended)

```bash
# Build source distribution and wheel
uv build

# Publish to PyPI (requires PyPI credentials configured)
uv publish
```

#### Using Traditional Tools

```bash
# Build with hatchling
python -m pip install build
python -m build

# Publish with twine
python -m pip install twine
twine upload dist/*
```

## Python Compatibility

This package requires Python 3.9+ and uses type hints compatible with older Python versions:

- Use `Optional[str]` instead of `str | None`
- Use `List[str]` instead of `list[str]`
- Import from `typing` module

## License

See LICENSE file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass and coverage is maintained
5. Submit a pull request

## Roadmap

- [ ] Publish to PyPI
- [ ] Add more validators (mypy, ruff, pytest)
- [ ] Support for custom validator plugins
- [ ] Improved error messages with suggestions
- [ ] Performance optimizations for large repositories
