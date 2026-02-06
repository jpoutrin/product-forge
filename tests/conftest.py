"""Pytest configuration and shared fixtures."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_spec_file(temp_dir: Path) -> Path:
    """Create a sample spec file for testing."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    spec_file = spec_dir / "test-spec.md"
    spec_file.write_text("""# Test Specification

## Objective
This is a test objective.

## Task Description
This describes the task.

## Implementation
Details here.
""")
    return spec_file


@pytest.fixture
def sample_plan_file(temp_dir: Path) -> Path:
    """Create a sample task orchestration plan file."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    plan_file = spec_dir / "test-plan.md"
    plan_file.write_text("""# Task Orchestration Plan

## File Ownership Matrix

| File | CREATE | MODIFY (Scope) | Task | Wave |
|------|--------|----------------|------|------|
| src/foo.py | task-1 | - | task-1 | 1 |
| src/bar.py | task-2 | - | task-2 | 1 |
| tests/test_foo.py | task-3 | - | task-3 | 2 |

## Tasks

### Task 1: Create Foo

**Task ID:** task-1
**Wave:** 1
**File Ownership:**
- CREATE: src/foo.py
- MODIFY: -
- BOUNDARY: src/bar.py

### Task 2: Create Bar

**Task ID:** task-2
**Wave:** 1
**File Ownership:**
- CREATE: src/bar.py
- MODIFY: -
- BOUNDARY: src/foo.py

### Task 3: Test Foo

**Task ID:** task-3
**Wave:** 2
**File Ownership:**
- CREATE: tests/test_foo.py
- MODIFY: -
- BOUNDARY: src/foo.py, src/bar.py
""")
    return plan_file
