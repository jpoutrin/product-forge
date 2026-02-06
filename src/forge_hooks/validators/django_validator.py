"""Django validation for comprehensive project quality checks."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..common.hook_io import HookResult


class DjangoValidator:
    """Validates Django projects with type checking, linting, tests, and Django checks."""

    def __init__(
        self,
        files: Optional[str] = None,
        skip_mypy: bool = False,
        skip_ruff: bool = False,
        skip_tests: bool = False,
        skip_django_checks: bool = False,
        coverage_threshold: int = 80,
    ):
        """
        Initialize Django validator.

        Args:
            files: Files or directory to validate (default: current directory)
            skip_mypy: Skip type checking
            skip_ruff: Skip linting
            skip_tests: Skip unit tests
            skip_django_checks: Skip Django system checks
            coverage_threshold: Minimum coverage percentage (default: 80)
        """
        self.files = files or "."
        self.skip_mypy = skip_mypy
        self.skip_ruff = skip_ruff
        self.skip_tests = skip_tests
        self.skip_django_checks = skip_django_checks
        self.coverage_threshold = coverage_threshold
        self.validation_errors = []

    def validate(self) -> HookResult:
        """Run all Django validation checks."""

        # Detect if this is a uv project
        uv_prefix = self._get_uv_prefix()

        # Check if this is a Django project
        is_django = Path("manage.py").exists()

        # Run validations
        checks = [
            ("Type checking (mypy)", self._run_mypy, not self.skip_mypy),
            ("Linting (ruff)", self._run_ruff, not self.skip_ruff),
            ("Unit tests (pytest)", self._run_pytest, not self.skip_tests),
            ("Django system checks", self._run_django_checks, is_django and not self.skip_django_checks),
            ("Migration validation", self._run_migration_check, is_django and not self.skip_django_checks),
        ]

        for name, check_fn, should_run in checks:
            if should_run:
                success = check_fn(uv_prefix)
                if not success:
                    self.validation_errors.append(name)

        # Return results
        if self.validation_errors:
            return HookResult(
                ok=False,
                result="block",
                message=f"Validation failed: {', '.join(self.validation_errors)}",
            )

        return HookResult(
            ok=True,
            result="continue",
            message="All Django validations passed",
        )

    def _get_uv_prefix(self) -> str:
        """Detect if using uv and return appropriate prefix."""
        if Path("pyproject.toml").exists():
            try:
                subprocess.run(["uv", "--version"], capture_output=True, check=True)
                return "uv run "
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        return ""

    def _run_mypy(self, uv_prefix: str) -> bool:
        """Run mypy type checking."""
        cmd = f"{uv_prefix}mypy {self.files}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Check if command not found
        if "command not found" in result.stderr or "not found" in result.stderr:
            print("⚠️  mypy not found - skipping type checks", file=sys.stderr)
            return True

        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0

    def _run_ruff(self, uv_prefix: str) -> bool:
        """Run ruff linting."""
        cmd = f"{uv_prefix}ruff check {self.files}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Check if command not found
        if "command not found" in result.stderr or "not found" in result.stderr:
            print("⚠️  ruff not found - skipping linting", file=sys.stderr)
            return True

        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0

    def _run_pytest(self, uv_prefix: str) -> bool:
        """Run pytest with coverage requirements."""
        cmd = f"{uv_prefix}pytest --cov --cov-fail-under={self.coverage_threshold} -v"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Check if command not found
        if "command not found" in result.stderr or "not found" in result.stderr:
            print("⚠️  pytest not found - skipping tests", file=sys.stderr)
            return True

        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0

    def _run_django_checks(self, uv_prefix: str) -> bool:
        """Run Django system checks."""
        try:
            cmd = f"{uv_prefix}python manage.py check --deploy"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def _run_migration_check(self, uv_prefix: str) -> bool:
        """Run migration consistency check."""
        try:
            cmd = f"{uv_prefix}python manage.py makemigrations --check --dry-run"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
