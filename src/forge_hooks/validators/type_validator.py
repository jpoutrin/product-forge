"""Type checking validator using mypy."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..common.hook_io import HookResult


class TypeValidator:
    """Validates Python code with mypy type checking."""

    def __init__(
        self,
        files: Optional[str] = None,
        strict: bool = False,
    ):
        """
        Initialize Type validator.

        Args:
            files: Files or directory to validate (default: current directory)
            strict: Use strict type checking mode
        """
        self.files = files or "."
        self.strict = strict

    def validate(self) -> HookResult:
        """Run mypy type checking."""

        # Detect if this is a uv project
        uv_prefix = self._get_uv_prefix()

        # Run mypy
        success = self._run_mypy(uv_prefix)

        if not success:
            return HookResult(
                ok=False,
                result="block",
                message="Type checking failed",
            )

        return HookResult(
            ok=True,
            result="continue",
            message="Type checking passed",
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
        strict_flag = "--strict" if self.strict else ""
        cmd = f"{uv_prefix}mypy {strict_flag} {self.files}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Check if command not found
        if "command not found" in result.stderr or "not found" in result.stderr:
            print("⚠️  mypy not found - please install mypy", file=sys.stderr)
            return False

        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
