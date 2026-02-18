"""Session statistics tracking."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SessionStats:
    """Statistics about captured sessions."""

    total: int
    processed: int
    by_project: dict[str, int]
    last_session: Optional[str]

    @classmethod
    def load(cls, stats_file: Path) -> "SessionStats":
        """
        Load stats from session_stats.json.

        Args:
            stats_file: Path to session_stats.json

        Returns:
            SessionStats instance
        """
        if not stats_file.exists():
            return cls(
                total=0,
                processed=0,
                by_project={},
                last_session=None,
            )

        data = json.loads(stats_file.read_text())
        return cls(
            total=data.get("total_sessions", 0),
            processed=data.get("processed_sessions", 0),
            by_project=data.get("by_project", {}),
            last_session=data.get("last_session"),
        )

    def save(self, stats_file: Path) -> None:
        """
        Save stats to session_stats.json.

        Args:
            stats_file: Path to session_stats.json
        """
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "total_sessions": self.total,
            "processed_sessions": self.processed,
            "by_project": self.by_project,
            "last_session": self.last_session,
        }
        stats_file.write_text(json.dumps(data, indent=2))

    def update(self, project: str, captured_at: str) -> None:
        """
        Update stats with new session.

        Args:
            project: Project slug
            captured_at: ISO format timestamp
        """
        self.total += 1
        self.by_project[project] = self.by_project.get(project, 0) + 1
        self.last_session = captured_at

    def mark_processed(self) -> None:
        """Mark a session as processed."""
        self.processed += 1
