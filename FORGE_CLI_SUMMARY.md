# forge CLI - Product Forge Command-Line Tool

**Status**: ✅ **Successfully Deployed**
**Version**: 0.1.0
**Command**: `forge`
**Installation**: Global (user-wide)
**Location**: `/Users/jeremiepoutrin/.local/bin/forge`

---

## What is `forge`?

The `forge` CLI is the unified command-line tool for Product Forge. It provides validators, utilities, and tools for working with Product Forge plugins, skills, and workflows.

**Previously named:** `forge-hooks` (renamed to `forge` for simplicity)

---

## Installation

### Global Installation (Recommended)

```bash
# From the Product Forge directory
uv tool install .

# Verify installation
forge --version
# Output: forge, version 0.1.0
```

### Local Development Installation

```bash
# Install with all development dependencies
uv sync --all-extras

# Run locally with uv run
uv run forge --help
```

---

## Available Commands

### Validation Commands

The `forge validate` command group provides file validation tools:

#### 1. New File Validator

Validates that a new file was created in a directory.

```bash
forge validate new-file --directory specs --extension .md
```

**Options:**
- `-d, --directory` - Directory to check (default: specs)
- `-e, --extension` - File extension to match (default: .md)
- `--max-age` - Maximum file age in minutes (default: 5)

**Use cases:**
- Hook validation after creating PRDs, Tech Specs, RFCs
- CI/CD verification of generated files
- Ensuring output files are created

#### 2. Contains Validator

Validates that a file contains required content.

```bash
forge validate contains \
  --directory specs \
  --extension .md \
  --contains "## Objective" \
  --contains "## Task Description"
```

**Options:**
- `-d, --directory` - Directory to check (default: specs)
- `-e, --extension` - File extension to match (default: .md)
- `--contains` - Required string (can be used multiple times)
- `--max-age` - Maximum file age in minutes (default: 5)

**Use cases:**
- Validate document structure and required sections
- Ensure PRDs have all required headings
- Check for compliance with templates

#### 3. Ownership Validator

Validates file ownership rules in task orchestration plans.

```bash
forge validate ownership --directory specs --extension .md
```

**Options:**
- `-d, --directory` - Directory to check (default: specs)
- `-e, --extension` - File extension to match (default: .md)
- `--max-age` - Maximum file age in minutes (default: 5)

**Validation rules:**
1. Each file is CREATEd by at most one task
2. Parallel tasks (same wave) with unscoped MODIFY target different files
3. Parallel tasks with scoped MODIFY have non-overlapping scopes
4. No task modifies files in its BOUNDARY list

**Use cases:**
- Validate parallel task plans before execution
- Prevent file conflicts in multi-agent workflows
- Ensure proper task isolation

---

## Output Format

All validators return JSON output compatible with Claude Code hooks:

```json
{
  "ok": true,
  "result": "continue",
  "message": "Validation passed"
}
```

**Exit codes:**
- `0` - Validation passed (success)
- `1` - Validation failed (error)

**Result values:**
- `"continue"` - Validation passed, proceed
- `"block"` - Validation failed, stop execution

---

## Usage in Hooks

The `forge` CLI is designed to be used in Claude Code skill hooks:

```yaml
hooks:
  Stop:
    - type: command
      command: >-
        forge validate new-file --directory specs --extension .md
```

**Advantages:**
- Simple, clean command syntax
- No need for `uv run` or Python interpreter
- Consistent error handling
- Proper exit codes for hook flow control

---

## Architecture

### Package Structure

```
src/forge_hooks/
├── __init__.py
├── cli.py                    # Main CLI entry point
├── common/                   # Shared utilities
│   ├── __init__.py
│   ├── file_discovery.py    # File finding utilities
│   ├── git_utils.py         # Git integration
│   └── hook_io.py           # JSON output formatting
└── validators/               # Validator implementations
    ├── __init__.py
    ├── base.py              # Base validator class
    ├── contains.py          # Content validator
    ├── new_file.py          # New file validator
    └── ownership.py         # Ownership validator
```

### Technology Stack

- **Python**: 3.9+ (backward compatible)
- **CLI Framework**: Click 8.0+
- **Testing**: pytest 7.0+
- **Build System**: Hatchling (PEP 517)
- **Package Manager**: uv

---

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=forge_hooks --cov-report=term-missing
```

**Current test metrics:**
- 43 tests total
- 100% passing
- 77% code coverage
- ~0.44s execution time

### Making Changes

The package is installed in **editable mode** for local development:

1. Edit source files in `src/forge_hooks/`
2. Run tests: `uv run pytest`
3. Test CLI locally: `uv run forge <command>`
4. Update global installation: `uv tool install . --force`

No reinstall needed for local testing!

### Adding New Validators

1. Create new validator in `src/forge_hooks/validators/`
2. Inherit from `BaseValidator`
3. Implement `validate()` method
4. Add CLI command in `src/forge_hooks/cli.py`
5. Write tests in `tests/validators/`

**Example validator:**

```python
from .base import BaseValidator, HookResult

class MyValidator(BaseValidator):
    def validate(self) -> HookResult:
        # Your validation logic here
        if validation_passed:
            return HookResult.success("Validation passed")
        else:
            return HookResult.block("Validation failed")
```

---

## Future Enhancements

See `FORGE_CLI_EXPANSION_PLAN.md` for planned additions:

### Phase 1: Additional Utilities (Planned)
- Marketplace validator
- Forge index generator
- YouTube transcript fetcher
- Feedback manager

### Phase 2: Enhanced Features (Planned)
- JSON/YAML validation
- Plugin scaffolding
- Hook testing utilities
- Performance profiling

---

## Comparison: Before vs After Rename

### Before (forge-hooks)

```bash
# Verbose, hooks-specific naming
forge-hooks validate new-file --directory specs --extension .md
```

**Issues:**
- Name implies only for hooks (too narrow)
- Longer to type
- Less memorable

### After (forge)

```bash
# Clean, simple, memorable
forge validate new-file --directory specs --extension .md
```

**Benefits:**
- ✅ Shorter, easier to type
- ✅ Name aligns with "Product Forge" brand
- ✅ Flexible for expanding beyond hooks
- ✅ More professional CLI name

---

## Files

**Package configuration:**
- `pyproject.toml` - Package metadata and dependencies

**Source code:**
- `src/forge_hooks/` - Main package directory

**Documentation:**
- `FORGE_CLI_README.md` - Detailed usage guide
- `FORGE_CLI_SUMMARY.md` - This file (quick reference)
- `FORGE_CLI_EXPANSION_PLAN.md` - Future roadmap
- `DEPLOYMENT_SUMMARY.md` - Deployment details

**Tests:**
- `tests/` - Test suite (43 tests, 77% coverage)

---

## Troubleshooting

### Command not found

**Problem:** `forge: command not found`

**Solution 1:** Ensure `~/.local/bin` is in your PATH

```bash
echo $PATH | grep -q ".local/bin" && echo "✓ PATH OK" || echo "✗ Add to PATH"

# Add to PATH (if needed)
export PATH="$HOME/.local/bin:$PATH"
```

**Solution 2:** Reinstall globally

```bash
uv tool install . --force
```

### Import errors

**Problem:** Module import errors when running CLI

**Solution:** Reinstall package

```bash
uv sync --all-extras --reinstall
uv tool install . --force
```

### Tests fail

**Problem:** Tests not passing

**Solution:** Check Python version

```bash
python --version  # Should be 3.9+
uv run pytest -v --tb=short
```

---

## Quick Reference

```bash
# Help
forge --help
forge validate --help

# Version
forge --version

# Validate new file creation
forge validate new-file -d specs -e .md

# Validate file contents
forge validate contains -d specs -e .md --contains "## Objective"

# Validate ownership rules
forge validate ownership -d specs -e .md

# Run tests
uv run pytest

# Update global installation
uv tool install . --force
```

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Package name | Short & clean | `forge` | ✅ |
| Global install | User-wide | `~/.local/bin/forge` | ✅ |
| Tests passing | 43 | 43 | ✅ |
| Test coverage | >70% | 77% | ✅ |
| Execution time | <1s | 0.44s | ✅ |
| Validators working | 3 | 3 | ✅ |

---

**Last updated:** 2026-02-06
**Version:** 0.1.0
**Status:** Production-ready ✅
