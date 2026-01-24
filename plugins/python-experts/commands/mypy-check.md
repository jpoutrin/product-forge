---
description: Run Mypy type checking on Python code with detailed error reporting
argument-hint: [<path>] [--strict] [--html] [--install]
---

# mypy-check

**Category**: Python Development

## Usage

```bash
/mypy-check [<path>] [--strict] [--html] [--install]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<path>` | No | Path to check (default: current directory) |
| `--strict` | No | Use strict type checking mode |
| `--html` | No | Generate HTML coverage report |
| `--install` | No | Install Mypy if not present |

## Purpose

Run Mypy static type checker on Python code to:

1. **Detect Type Errors**: Find type mismatches before runtime
2. **Check Coverage**: Report type annotation coverage
3. **Enforce Standards**: Ensure type safety across codebase
4. **Generate Reports**: Create detailed HTML reports

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Parse Arguments

```
PATH = first positional argument or "."
STRICT_MODE = true if --strict specified
HTML_REPORT = true if --html specified
INSTALL_MYPY = true if --install specified
```

### 2. Check Mypy Installation

```bash
if ! command -v mypy &> /dev/null; then
    if [ "$INSTALL_MYPY" = true ]; then
        echo "Installing Mypy..."
        # Try uv first, then pip
        if command -v uv &> /dev/null; then
            uv pip install mypy
        else
            pip install mypy
        fi
    else
        echo "Error: Mypy not found. Run with --install to install."
        exit 1
    fi
fi
```

### 3. Determine Configuration

Check for existing Mypy configuration in order:

1. `mypy.ini`
2. `.mypy.ini`
3. `pyproject.toml` (with `[tool.mypy]` section)
4. `setup.cfg` (with `[mypy]` section)

### 4. Build Mypy Command

```bash
MYPY_CMD="mypy"

# Add path
MYPY_CMD="$MYPY_CMD $PATH"

# Show error codes and column numbers
MYPY_CMD="$MYPY_CMD --show-error-codes --show-column-numbers"

# Strict mode overrides
if [ "$STRICT_MODE" = true ]; then
    MYPY_CMD="$MYPY_CMD --strict"
fi

# HTML report
if [ "$HTML_REPORT" = true ]; then
    REPORT_DIR="./mypy-report"
    MYPY_CMD="$MYPY_CMD --html-report $REPORT_DIR"
fi
```

### 5. Run Mypy

Execute the type checker and capture output:

```bash
echo "Running Mypy type checker..."
echo "Command: $MYPY_CMD"
echo ""

$MYPY_CMD
EXIT_CODE=$?
```

### 6. Parse and Report Results

#### Success (Exit Code 0)

```
✓ Mypy Type Check Passed
===========================

Path: ./src
Configuration: mypy.ini
Files checked: 42
No type errors found!

Type coverage: 95.3%
```

#### Errors Found (Exit Code 1)

Parse Mypy output and categorize errors:

```
✗ Mypy Type Check Failed
==========================

Path: ./src
Configuration: mypy.ini
Files checked: 42

Errors by Category:
  [arg-type]        5 errors
  [return-value]    3 errors
  [assignment]      2 errors
  [attr-defined]    1 error

Errors by Severity:
  Error:   11
  Note:     3

Top Issues:
──────────────────────────────────────────────────────────
src/services/users.py:45:12: error: Argument 1 to "process"
has incompatible type "str | None"; expected "str"  [arg-type]

src/models/user.py:23:16: error: Incompatible return value
type (got "None", expected "User")  [return-value]

src/utils/helpers.py:67:5: error: Incompatible types in
assignment (expression has type "int", variable has type "str")
[assignment]
──────────────────────────────────────────────────────────

Total: 11 errors found in 7 files

Run with --html for detailed coverage report.
See: https://mypy.readthedocs.io/en/stable/error_codes.html
```

#### With HTML Report

```
✓ HTML Report Generated
========================

Report location: ./mypy-report/index.html

Open with:
  open ./mypy-report/index.html

The report shows:
  - Per-file type coverage
  - Unannotated functions
  - Any expressions used
  - Error locations with context
```

### 7. Provide Fix Suggestions

For common error types, suggest fixes:

```
Suggested Fixes:
────────────────

[arg-type] errors (5 found):
  • Add type guards: if x is not None: ...
  • Make parameter Optional: def func(x: str | None)
  • Use assert to narrow type: assert x is not None

[return-value] errors (3 found):
  • Update return type: -> User | None
  • Add early return check
  • Raise exception instead of returning None

[assignment] errors (2 found):
  • Check variable types match
  • Use type conversion: str(value)
  • Annotate variable: result: int = ...
```

### 8. Detect Common Issues

#### Missing Type Hints

```bash
# Check for functions without type hints
mypy --disallow-untyped-defs --no-error-summary "$PATH" 2>&1 | \
    grep "Function is missing a type annotation" | wc -l
```

Report:

```
Type Annotation Coverage:
  Functions with hints:     87 / 120 (72.5%)
  Functions missing hints:  33

Top files needing annotations:
  src/legacy/utils.py:      12 functions
  src/services/old_api.py:   8 functions
  src/helpers/common.py:     7 functions

Tip: Run '/mypy-setup --init' to add type hints incrementally
```

#### Any Usage

```bash
# Track 'Any' usage (type holes)
mypy --any-exprs-report ./any-report "$PATH"
```

### 9. Exit Codes

- `0`: No type errors found
- `1`: Type errors found
- `2`: Mypy configuration error

---

## Examples

```bash
# Check current directory
/mypy-check

# Check specific path
/mypy-check src/

# Strict mode (all checks enabled)
/mypy-check --strict

# Generate HTML coverage report
/mypy-check src/ --html

# Install and run
/mypy-check --install

# Full strict check with report
/mypy-check src/ --strict --html
```

## Configuration Detection

Claude Code should detect and report the active configuration:

```bash
# Check for mypy.ini
if [ -f "mypy.ini" ]; then
    echo "Configuration: mypy.ini"
    echo ""
    echo "Active settings:"
    grep -E "^(python_version|strict|warn_|disallow_)" mypy.ini | head -5
fi

# Check pyproject.toml
if [ -f "pypy.toml" ] && grep -q "\[tool.mypy\]" pyproject.toml; then
    echo "Configuration: pyproject.toml [tool.mypy]"
fi

# No config found
if [ ! -f "mypy.ini" ] && ! grep -q "\[tool.mypy\]" pyproject.toml 2>/dev/null; then
    echo "⚠ No Mypy configuration found"
    echo "Run '/mypy-setup' to create one"
fi
```

## Integration with Other Tools

### Pre-commit Hook

If `.pre-commit-config.yaml` exists, suggest adding Mypy:

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [types-requests]
```

### CI/CD Integration

Suggest GitHub Actions workflow:

```yaml
name: Type Check
on: [push, pull_request]
jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install mypy
      - run: mypy src/
```

## Common Error Patterns

Claude Code should recognize and explain common errors:

| Error Code | Common Cause | Fix |
|------------|--------------|-----|
| `arg-type` | Passing wrong type to function | Add type guard or convert type |
| `return-value` | Return type mismatch | Update return annotation |
| `assignment` | Variable type mismatch | Match types or use cast |
| `attr-defined` | Attribute doesn't exist | Check spelling or add to Protocol |
| `import-untyped` | Third-party lacks stubs | Add `# type: ignore[import-untyped]` |
| `no-any-return` | Function returns Any | Add explicit return type |

## Performance Tips

For large codebases:

```bash
# Use cache for faster subsequent runs
mypy --cache-dir=.mypy_cache src/

# Check only modified files
git diff --name-only | grep ".py$" | xargs mypy

# Parallel type checking (Mypy daemon)
dmypy run -- src/
```

## Related Skills

| Skill | Purpose |
|-------|---------|
| `python-experts:python-mypy` | Mypy type checking patterns |
| `python-experts:python-style` | Python coding standards |
| `python-experts:python-code-review` | Code review guidelines |

## Related Commands

| Command | Purpose |
|---------|---------|
| `/mypy-setup` | Configure Mypy in project |
| `/python-experts:review-django-commands` | Review Django commands |

## Troubleshooting

### Mypy Too Strict

```bash
# Start with basic checks
mypy --ignore-missing-imports src/

# Gradually enable strict checks
mypy --no-strict-optional src/
```

### Missing Type Stubs

```bash
# Install type stubs for common libraries
pip install types-requests types-PyYAML types-redis

# Or use Mypy's stub installer
mypy --install-types
```

### Performance Issues

```bash
# Skip cache directory
mypy --exclude=".mypy_cache" src/

# Limit recursion depth
mypy --follow-imports=skip src/
```
