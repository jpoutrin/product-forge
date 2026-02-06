"""Tests for file contains validator."""

from pathlib import Path

from forge_hooks.validators.contains import FileContainsValidator


def test_contains_validator_no_file(temp_dir: Path):
    """Test validator fails when no file exists."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    validator = FileContainsValidator(str(spec_dir), ".md", ["## Objective"], 5)
    result = validator.validate()

    assert not result.is_success
    assert result.result == "block"
    assert "No new file found" in result.reason


def test_contains_validator_file_with_content(temp_dir: Path):
    """Test validator succeeds when file contains required strings."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text("""# Specification

## Objective
This is the objective.

## Implementation
Details here.
""")

    validator = FileContainsValidator(
        str(spec_dir), ".md", ["## Objective", "## Implementation"], 5
    )
    result = validator.validate()

    assert result.is_success
    assert result.result == "continue"
    assert "contains all" in result.message.lower()


def test_contains_validator_missing_content(temp_dir: Path):
    """Test validator fails when content is missing."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text("""# Specification

## Objective
This is the objective.
""")

    validator = FileContainsValidator(
        str(spec_dir), ".md", ["## Objective", "## Implementation", "## Testing"], 5
    )
    result = validator.validate()

    assert not result.is_success
    assert result.result == "block"
    assert "missing" in result.reason.lower()
    assert "## Implementation" in result.reason
    assert "## Testing" in result.reason


def test_contains_validator_case_sensitive(temp_dir: Path):
    """Test validator is case-sensitive."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text("""# Specification

## objective
Lowercase objective.
""")

    validator = FileContainsValidator(
        str(spec_dir),
        ".md",
        ["## Objective"],  # Capital O
        5,
    )
    result = validator.validate()

    # Should fail because case doesn't match
    assert not result.is_success


def test_contains_validator_empty_requirements(temp_dir: Path):
    """Test validator succeeds with no content requirements."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text("# Any content")

    validator = FileContainsValidator(str(spec_dir), ".md", [], 5)
    result = validator.validate()

    assert result.is_success
    assert "no content checks" in result.message.lower()


def test_contains_validator_partial_match(temp_dir: Path):
    """Test validator requires exact substring match."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text("## Object")  # Missing 'ive'

    validator = FileContainsValidator(str(spec_dir), ".md", ["## Objective"], 5)
    result = validator.validate()

    # Should fail - partial match not enough
    assert not result.is_success
