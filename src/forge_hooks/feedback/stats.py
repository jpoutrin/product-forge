"""Feedback statistics tracking."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

FEEDBACK_TYPES = ["improvement", "skill-idea", "command-idea", "bug-report", "pattern"]


@dataclass
class FeedbackStats:
    """Statistics about collected feedback."""

    total: int
    by_type: dict[str, int]
    by_project: dict[str, int]
    last_updated: str

    @classmethod
    def load(cls, stats_file: Path) -> "FeedbackStats":
        """
        Load stats from stats.json.

        Args:
            stats_file: Path to stats.json

        Returns:
            FeedbackStats instance
        """
        if not stats_file.exists():
            return cls(
                total=0,
                by_type=dict.fromkeys(FEEDBACK_TYPES, 0),
                by_project={},
                last_updated=datetime.now().isoformat(),
            )

        data = json.loads(stats_file.read_text())
        return cls(
            total=data.get("total_feedback", 0),
            by_type=data.get("by_type", dict.fromkeys(FEEDBACK_TYPES, 0)),
            by_project=data.get("by_project", {}),
            last_updated=data.get("last_updated", datetime.now().isoformat()),
        )

    def save(self, stats_file: Path) -> None:
        """
        Save stats to stats.json.

        Args:
            stats_file: Path to stats.json
        """
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "total_feedback": self.total,
            "by_type": self.by_type,
            "by_project": self.by_project,
            "last_updated": self.last_updated,
        }
        stats_file.write_text(json.dumps(data, indent=2))

    def update(self, feedback_type: str, project: str) -> None:
        """
        Update stats with new feedback.

        Args:
            feedback_type: Type of feedback
            project: Project slug
        """
        self.total += 1
        self.by_type[feedback_type] = self.by_type.get(feedback_type, 0) + 1
        self.by_project[project] = self.by_project.get(project, 0) + 1
        self.last_updated = datetime.now().isoformat()
