"""Hook I/O utilities for reading input and writing results."""

import json
import sys
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class HookResult:
    """Standard hook result structure for Claude Code hooks."""

    ok: bool = True
    result: str = "continue"  # "continue" | "block"
    message: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}

    def to_json(self) -> str:
        """Serialize to JSON for hook output."""
        return json.dumps(self.to_dict())

    @property
    def is_success(self) -> bool:
        """Check if this result allows continuation."""
        return self.result == "continue"

    @property
    def exit_code(self) -> int:
        """Get appropriate exit code (0 for continue, 1 for block)."""
        return 0 if self.is_success else 1


def read_hook_input() -> dict:
    """
    Read and parse JSON from stdin.

    Returns:
        dict: Parsed JSON data, or empty dict if no input or invalid JSON.
    """
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return {}


def output_result(result: HookResult) -> None:
    """
    Print result JSON to stdout.

    Args:
        result: The HookResult to output.
    """
    print(result.to_json())
