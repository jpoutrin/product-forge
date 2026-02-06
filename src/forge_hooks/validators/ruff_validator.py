"""Ruff linting validator for code quality checks."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..common.hook_io import HookResult


class RuffValidator:
    """Validates Python code with ruff linting."""

    def __init__(
        self,
        files: Optional[str] = None,
        fix: bool = False,
    ):
        """
        Initialize Ruff validator.

        Args:
            files: Files or directory to validate (default: current directory)
            fix: Automatically fix issues when possible
        """
        self.files = files or "."
        self.fix = fix

    def validate(self) -> HookResult:
        """Run ruff linting."""

        # Detect if this is a uv project
        uv_prefix = self._get_uv_prefix()

        # Run ruff
        success = self._run_ruff(uv_prefix)

        if not success:
            return HookResult(
                ok=False,
                result="block",
                message="Ruff linting failed",
            )

        return HookResult(
            ok=True,
            result="continue",
            message="Ruff linting passed",
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

    def _run_ruff(self, uv_prefix: str) -> bool:
        """Run ruff linting."""
        fix_flag = "--fix" if self.fix else ""
        cmd = f"{uv_prefix}ruff check {fix_flag} {self.files}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Check if command not found
        if "command not found" in result.stderr or "not found" in result.stderr:
            print("⚠️  ruff not found - please install ruff", file=sys.stderr)
            return False

        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
