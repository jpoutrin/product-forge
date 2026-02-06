"""Tests for file ownership validator."""

from pathlib import Path

from forge_hooks.validators.ownership import (
    FileOwnershipValidator,
    parse_scope,
    scopes_overlap,
)


def test_parse_scope_simple():
    """Test parsing simple filename without scope."""
    filename, scope = parse_scope("file.py")
    assert filename == "file.py"
    assert scope is None


def test_parse_scope_with_class():
    """Test parsing file with class scope."""
    filename, scope = parse_scope("file.py::MyClass")
    assert filename == "file.py"
    assert scope == "MyClass"


def test_parse_scope_with_method():
    """Test parsing file with method scope."""
    filename, scope = parse_scope("file.py::MyClass.my_method")
    assert filename == "file.py"
    assert scope == "MyClass.my_method"


def test_parse_scope_with_whitespace():
    """Test parsing handles whitespace."""
    filename, scope = parse_scope("  file.py :: MyClass  ")
    assert filename == "file.py"
    assert scope == "MyClass"


def test_scopes_overlap_both_none():
    """Test unscoped always overlaps."""
    assert scopes_overlap(None, None)


def test_scopes_overlap_one_none():
    """Test scoped and unscoped overlap."""
    assert scopes_overlap(None, "MyClass")
    assert scopes_overlap("MyClass", None)


def test_scopes_overlap_identical():
    """Test identical scopes overlap."""
    assert scopes_overlap("MyClass", "MyClass")
    assert scopes_overlap("MyClass.method", "MyClass.method")


def test_scopes_overlap_nested():
    """Test nested scopes overlap."""
    assert scopes_overlap("MyClass", "MyClass.method")
    assert scopes_overlap("MyClass.method", "MyClass")


def test_scopes_no_overlap():
    """Test different scopes don't overlap."""
    assert not scopes_overlap("ClassA", "ClassB")
    assert not scopes_overlap("ClassA.method1", "ClassA.method2")


def test_ownership_validator_no_file(temp_dir: Path):
    """Test validator fails when no plan file exists."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert not result.is_success
    assert "No plan file found" in result.reason


def test_ownership_validator_valid_plan(sample_plan_file: Path):
    """Test validator succeeds with valid plan."""
    spec_dir = sample_plan_file.parent
    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert result.is_success
    assert "passed" in result.message.lower()


def test_ownership_validator_rule1_violation(temp_dir: Path):
    """Test Rule 1: File created by multiple tasks."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    plan_file = spec_dir / "plan.md"
    plan_file.write_text("""# Plan

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
- CREATE: src/foo.py
- MODIFY: -
- BOUNDARY: -
""")

    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert not result.is_success
    assert "Rule 1 violation" in result.reason
    assert "src/foo.py" in result.reason


def test_ownership_validator_rule23_violation_unscoped(temp_dir: Path):
    """Test Rule 2/3: Parallel tasks modify same file (unscoped)."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    plan_file = spec_dir / "plan.md"
    plan_file.write_text("""# Plan

### Task 1
**Task ID:** task-1
**Wave:** 1
**File Ownership:**
- CREATE: -
- MODIFY: src/foo.py
- BOUNDARY: -

### Task 2
**Task ID:** task-2
**Wave:** 1
**File Ownership:**
- CREATE: -
- MODIFY: src/foo.py
- BOUNDARY: -
""")

    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert not result.is_success
    assert "Rule 2/3 violation" in result.reason
    assert "unscoped" in result.reason


def test_ownership_validator_rule23_no_violation_scoped(temp_dir: Path):
    """Test Rule 2/3: Parallel tasks with non-overlapping scopes OK."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    plan_file = spec_dir / "plan.md"
    plan_file.write_text("""# Plan

### Task 1
**Task ID:** task-1
**Wave:** 1
**File Ownership:**
- CREATE: -
- MODIFY: src/foo.py::ClassA
- BOUNDARY: -

### Task 2
**Task ID:** task-2
**Wave:** 1
**File Ownership:**
- CREATE: -
- MODIFY: src/foo.py::ClassB
- BOUNDARY: -
""")

    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    # Should succeed - different scopes
    assert result.is_success


def test_ownership_validator_rule4_violation(temp_dir: Path):
    """Test Rule 4: Task modifies file in its BOUNDARY."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    plan_file = spec_dir / "plan.md"
    plan_file.write_text("""# Plan

### Task 1
**Task ID:** task-1
**Wave:** 1
**File Ownership:**
- CREATE: -
- MODIFY: src/foo.py, src/bar.py
- BOUNDARY: src/bar.py
""")

    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert not result.is_success
    assert "Rule 4 violation" in result.reason
    assert "src/bar.py" in result.reason


def test_ownership_validator_empty_plan(temp_dir: Path):
    """Test validator handles plan with no tasks."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    plan_file = spec_dir / "plan.md"
    plan_file.write_text("# Empty Plan\n\nNo tasks here.")

    validator = FileOwnershipValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    # Should succeed - nothing to validate
    assert result.is_success
    assert "No tasks found" in result.message
