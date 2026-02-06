"""Tests for new file validator."""

from pathlib import Path

from forge_hooks.validators.new_file import NewFileValidator


def test_new_file_validator_no_files(temp_dir: Path):
    """Test validator fails when no files exist."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    validator = NewFileValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert not result.is_success
    assert result.result == "block"
    assert "No new file found" in result.reason


def test_new_file_validator_recent_file(temp_dir: Path):
    """Test validator succeeds with recent file."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    # Create a recent file
    new_file = spec_dir / "new-spec.md"
    new_file.write_text("# New Spec")

    validator = NewFileValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert result.is_success
    assert result.result == "continue"
    assert "found" in result.message.lower()


def test_new_file_validator_wrong_extension(temp_dir: Path):
    """Test validator ignores files with wrong extension."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    # Create file with wrong extension
    (spec_dir / "file.txt").write_text("Text file")

    validator = NewFileValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert not result.is_success


def test_new_file_validator_multiple_files(temp_dir: Path):
    """Test validator succeeds with multiple matching files."""
    spec_dir = temp_dir / "specs"
    spec_dir.mkdir()

    (spec_dir / "file1.md").write_text("# File 1")
    (spec_dir / "file2.md").write_text("# File 2")

    validator = NewFileValidator(str(spec_dir), ".md", 5)
    result = validator.validate()

    assert result.is_success
