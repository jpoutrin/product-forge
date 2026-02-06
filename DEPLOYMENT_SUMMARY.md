# forge-hooks CLI - Local Deployment Summary

**Status**: ✅ **Successfully Deployed (Global Installation)**
**Date**: 2026-02-06
**Version**: 0.1.0
**Installation Path**: `/Users/jeremiepoutrin/.local/bin/forge-hooks`

> **Note**: The package is installed in two ways:
> 1. **Locally (editable)** - For development and testing (`uv sync --all-extras`)
> 2. **Globally (user-wide)** - For system-wide use (`uv tool install .`)
>
> When making code changes, the local editable version is updated automatically,
> but the global installation needs to be refreshed with `uv tool install . --force`.

---

## Deployment Results

### ✅ Local Installation (Development)

```bash
uv sync --all-extras
```

**Result:**
- Virtual environment created at `.venv/`
- Package `forge-hooks==0.1.0` installed in editable mode
- All dependencies installed (click, pytest, pytest-cov, etc.)
- CLI entry point configured successfully

### ✅ Global Installation (User-Wide)

```bash
uv tool install .
```

**Result:**
- Package installed globally at `~/.local/bin/forge-hooks`
- Available system-wide without `uv run` prefix
- Automatically added to PATH
- Can be used from any directory

### ✅ CLI Available Globally

The `forge-hooks` command is available system-wide (no prefix needed):

```bash
$ forge-hooks --version
forge-hooks, version 0.1.0

$ which forge-hooks
/Users/jeremiepoutrin/.local/bin/forge-hooks

$ forge-hooks --help
Usage: forge-hooks [OPTIONS] COMMAND [ARGS]...

  Product Forge hook utilities and validators.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  validate  File validation commands.
```

### ✅ All Validators Available

Three validators are fully functional:

1. **new-file** - Validates that a new file was created
2. **contains** - Validates file content requirements
3. **ownership** - Validates file ownership rules in task plans

```bash
$ uv run forge-hooks validate --help
Usage: forge-hooks validate [OPTIONS] COMMAND [ARGS]...

  File validation commands.

Commands:
  contains   Validate that a file contains required content.
  new-file   Validate that a new file was created.
  ownership  Validate file ownership rules in task orchestration plans.
```

### ✅ All Tests Pass

```bash
$ uv run pytest -v
============================== 43 passed in 0.47s ==============================
```

**Test Coverage:**
- 43 tests total
- All tests passing
- 77% code coverage
- 0.47 seconds execution time

**Coverage Details:**
```
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
src/forge_hooks/__init__.py                    3      0   100%
src/forge_hooks/cli.py                        42     42     0%   (CLI interface - expected)
src/forge_hooks/common/__init__.py             4      0   100%
src/forge_hooks/common/file_discovery.py      49      6    88%
src/forge_hooks/common/git_utils.py           23     13    43%
src/forge_hooks/common/hook_io.py             28      5    82%
src/forge_hooks/validators/__init__.py         5      0   100%
src/forge_hooks/validators/base.py            23      9    61%
src/forge_hooks/validators/contains.py        52      3    94%
src/forge_hooks/validators/new_file.py        25      3    88%
src/forge_hooks/validators/ownership.py      136      7    95%
------------------------------------------------------------------------
TOTAL                                        390     88    77%
```

### ✅ Functional Verification

Validators execute correctly and return proper JSON output (works globally):

```bash
$ forge-hooks validate new-file --directory specs --extension .md
{
  "ok": true,
  "result": "block",
  "reason": "VALIDATION FAILED: No new file found matching specs/*.md..."
}
```

**Exit codes:**
- Success (validation passed): Exit code 0
- Failure (validation failed): Exit code 1

**Works from any directory** - no need to be in the project directory!

---

## Usage

### Running Validators (Global - Recommended)

Validators can be run directly from any directory:

```bash
# New file validator
forge-hooks validate new-file --directory specs --extension .md

# Contains validator
forge-hooks validate contains \
  --directory specs \
  --extension .md \
  --contains "## Objective" \
  --contains "## Task Description"

# Ownership validator
forge-hooks validate ownership --directory specs --extension .md
```

### Running Validators (Local Development)

When developing or testing, use `uv run` to use the editable local version:

```bash
# Uses the local editable installation
uv run forge-hooks validate new-file --directory specs --extension .md
```

### Common Options

All validators support:
- `--directory` - Directory to search (default: specs)
- `--extension` - File extension to match (default: .md)
- `--max-age` - Maximum file age in minutes (default: 5)

### Integration with Hooks

Validators can be called directly from SKILL.md hooks (no prefix needed):

```yaml
hooks:
  Stop:
    - type: command
      command: >-
        forge-hooks validate new-file --directory specs --extension .md
```

This works because `forge-hooks` is installed globally at `~/.local/bin/forge-hooks`.

---

## Package Structure

```
/Users/jeremiepoutrin/projects/github/jpoutrin/product-forge/
├── pyproject.toml              # Package configuration
├── src/forge_hooks/            # Source code
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point
│   ├── common/                 # Shared utilities
│   │   ├── __init__.py
│   │   ├── file_discovery.py  # File finding utilities
│   │   ├── git_utils.py       # Git integration
│   │   └── hook_io.py         # JSON output formatting
│   └── validators/             # Validator implementations
│       ├── __init__.py
│       ├── base.py            # Base validator class
│       ├── contains.py        # Content validator
│       ├── new_file.py        # New file validator
│       └── ownership.py       # Ownership validator
└── tests/                      # Test suite (43 tests)
    ├── conftest.py
    ├── common/
    ├── validators/
    └── test_integration.py
```

---

## Development Workflow

### Making Changes

Since the package is installed in **editable mode**, changes to source files are immediately reflected:

1. Edit source files in `src/forge_hooks/`
2. Run tests: `uv run pytest`
3. Test CLI: `uv run forge-hooks validate ...`
4. No reinstall needed!

### Running Tests

```bash
# All tests
uv run pytest

# Verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=forge_hooks --cov-report=term-missing

# Specific test file
uv run pytest tests/validators/test_ownership.py -v
```

### Adding New Validators

1. Create new file in `src/forge_hooks/validators/`
2. Inherit from `BaseValidator`
3. Implement `validate()` method
4. Add CLI command in `src/forge_hooks/cli.py`
5. Write tests in `tests/validators/`
6. Update documentation

---

## Files Created During Deployment

- `.venv/` - Virtual environment (auto-created by uv)
- `.pytest_cache/` - Pytest cache
- `*.pyc` files in `__pycache__/` directories

All generated files are excluded from git via `.gitignore`.

---

## Next Steps

### ✅ Completed
1. Package installed in editable mode
2. CLI commands available via `uv run`
3. All 43 tests passing
4. Validators functional and tested

### 🔄 Optional Enhancements

1. **Update Hook Files** - Replace wrapper scripts with direct CLI calls in SKILL.md files
2. **Publish to PyPI** - Make package available for other projects
3. **Add More Validators** - Extend validation capabilities
4. **Improve Coverage** - Add CLI integration tests

---

## Troubleshooting

### Command not found

**Problem:** `forge-hooks: command not found`

**Solution 1:** Ensure `~/.local/bin` is in your PATH:
```bash
echo $PATH | grep -q ".local/bin" && echo "✓ PATH includes .local/bin" || echo "✗ Add ~/.local/bin to PATH"
```

**Solution 2:** Reinstall globally:
```bash
uv tool install . --force
```

**Solution 3:** Use `uv run` for local development:
```bash
uv run forge-hooks --help
```

### Import errors

**Problem:** Module import errors when running CLI

**Solution:** Reinstall package:
```bash
uv sync --all-extras --reinstall
```

### Tests fail

**Problem:** Tests not passing

**Solution:** Check Python version (3.9+ required):
```bash
python --version
uv run pytest -v --tb=short
```

---

## Documentation

- **Package README**: `FORGE_HOOKS_README.md`
- **Source Code**: `src/forge_hooks/`
- **Tests**: `tests/`
- **Plan**: `PHASE1_SUMMARY.md`

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Package installed locally | ✓ | ✓ (editable) | ✅ |
| Package installed globally | ✓ | ✓ (user-wide) | ✅ |
| CLI available globally | ✓ | ✓ at `~/.local/bin` | ✅ |
| Tests passing | 43 | 43 | ✅ |
| Test coverage | >70% | 77% | ✅ |
| Execution time | <1s | 0.47s | ✅ |
| Validators working | 3 | 3 | ✅ |

---

**Deployment Complete!** 🎉

The `forge-hooks` CLI is now fully functional and ready for use in Product Forge workflows.
