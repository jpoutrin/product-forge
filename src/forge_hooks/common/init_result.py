"""Value objects for tracking Product Forge initialization results."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


@dataclass
class SubsystemResult:
    """Result of initializing a single subsystem.

    Attributes:
        name: Human-readable subsystem name
        status: Initialization outcome (success/skipped/failed)
        reason: Optional explanation for skip or failure
        details: Additional context (file paths, versions, etc.)
    """

    name: str
    status: Literal["success", "skipped", "failed"]
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def is_success(self) -> bool:
        """Check if initialization succeeded."""
        return self.status == "success"

    def is_skipped(self) -> bool:
        """Check if initialization was skipped."""
        return self.status == "skipped"

    def is_failed(self) -> bool:
        """Check if initialization failed."""
        return self.status == "failed"


class InitializationResult:
    """Aggregated results from initializing all Product Forge subsystems.

    Tracks success, skip, and failure states for each subsystem and provides
    convenient methods for querying overall status and generating next steps.

    Example:
        >>> result = InitializationResult()
        >>> result.add_success("Browser capture", {"config": "~/.claude/..."})
        >>> result.add_skip("Webhook system", "already installed")
        >>> result.has_failures()
        False
        >>> result.get_successful()
        ['Browser capture']
    """

    def __init__(self) -> None:
        """Initialize empty result tracker."""
        self.results: List[SubsystemResult] = []

    def add_success(self, name: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Record successful initialization.

        Args:
            name: Subsystem name (e.g., "Browser capture system")
            details: Optional context (paths, versions, etc.)
        """
        self.results.append(SubsystemResult(name=name, status="success", details=details))

    def add_skip(self, name: str, reason: str) -> None:
        """Record skipped subsystem.

        Args:
            name: Subsystem name
            reason: Why it was skipped (e.g., "user declined", "already installed")
        """
        self.results.append(SubsystemResult(name=name, status="skipped", reason=reason))

    def add_failure(self, name: str, error: str) -> None:
        """Record failed initialization.

        Args:
            name: Subsystem name
            error: Error message or exception string
        """
        self.results.append(SubsystemResult(name=name, status="failed", reason=error))

    def has_failures(self) -> bool:
        """Check if any subsystem failed to initialize."""
        return any(r.is_failed() for r in self.results)

    def has_successes(self) -> bool:
        """Check if any subsystem initialized successfully."""
        return any(r.is_success() for r in self.results)

    def get_successful(self) -> List[str]:
        """Get names of successfully initialized subsystems."""
        return [r.name for r in self.results if r.is_success()]

    def get_skipped(self) -> List[str]:
        """Get names of skipped subsystems with reasons."""
        return [f"{r.name} ({r.reason})" if r.reason else r.name
                for r in self.results if r.is_skipped()]

    def get_failed(self) -> List[tuple[str, str]]:
        """Get names and error messages of failed subsystems."""
        return [(r.name, r.reason or "unknown error")
                for r in self.results if r.is_failed()]

    def get_next_steps(self) -> List[str]:
        """Generate contextual next steps based on what was initialized.

        Returns:
            List of actionable next steps for the user
        """
        steps = []
        successful = self.get_successful()

        if "Browser capture system" in successful:
            steps.append("Test browser capture: forge browser-capture --help")

        if "Feedback/learnings directory" in successful:
            steps.append("View feedback: forge feedback list")

        if "Webhook notification system" in successful:
            steps.append("Restart your shell: source ~/.zshrc")
            steps.append("Start Claude Code in tmux for notifications")

        # Always add general help if anything succeeded
        if steps:
            steps.append("Run 'forge --help' to see all available commands")

        return steps

    def __len__(self) -> int:
        """Return number of subsystems processed."""
        return len(self.results)

    def __bool__(self) -> bool:
        """Return True if any subsystems were processed."""
        return len(self.results) > 0
