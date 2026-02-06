"""Integration tests for forge-hooks validators."""

import tempfile
from pathlib import Path

from forge_hooks.validators import (
    FileContainsValidator,
    FileOwnershipValidator,
    NewFileValidator,
)


def test_new_file_validator_integration():
    """Integration test for NewFileValidator."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specs"
        spec_dir.mkdir()

        # Should fail initially
        validator = NewFileValidator(str(spec_dir), ".md", 5)
        result = validator.validate()
        assert not result.is_success

        # Create a file
        (spec_dir / "test.md").write_text("# Test")

        # Should succeed now
        result = validator.validate()
        assert result.is_success


def test_contains_validator_integration():
    """Integration test for FileContainsValidator."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specs"
        spec_dir.mkdir()

        # Create a file
        spec_file = spec_dir / "spec.md"
        spec_file.write_text("""# Specification

## Objective
This is the objective.

## Task Description
Describes the task.
""")

        # Should succeed with matching content
        validator = FileContainsValidator(
            str(spec_dir), ".md", ["## Objective", "## Task Description"], 5
        )
        result = validator.validate()
        assert result.is_success

        # Should fail with missing content
        validator2 = FileContainsValidator(
            str(spec_dir), ".md", ["## Objective", "## Missing Section"], 5
        )
        result2 = validator2.validate()
        assert not result2.is_success


def test_ownership_validator_integration():
    """Integration test for FileOwnershipValidator."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specs"
        spec_dir.mkdir()

        # Create a valid plan
        plan_file = spec_dir / "plan.md"
        plan_file.write_text("""# Task Plan

### Task 1
**Task ID:** task-1
**Wave:** 1
**File Ownership:**
- CREATE: src/foo.py
- MODIFY: -
- BOUNDARY: -

### Task 2
**Task ID:** task-2
**Wave:** 2
**File Ownership:**
- CREATE: src/bar.py
- MODIFY: src/foo.py::FooClass
- BOUNDARY: -
""")

        # Should succeed
        validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
        result = validator.validate()
        assert result.is_success


def test_validator_error_handling():
    """Test that validators handle errors gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / "specs"
        spec_dir.mkdir()

        # Create an invalid file (empty)
        (spec_dir / "empty.md").write_text("")

        # Validators should not crash
        validator1 = NewFileValidator(str(spec_dir), ".md", 5)
        result1 = validator1.validate()
        assert result1 is not None

        validator2 = FileContainsValidator(str(spec_dir), ".md", ["Test"], 5)
        result2 = validator2.validate()
        assert result2 is not None

        validator3 = FileOwnershipValidator(str(spec_dir), ".md", 5)
        result3 = validator3.validate()
        assert result3 is not None
