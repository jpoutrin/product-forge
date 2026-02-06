"""Core feedback management operations."""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .stats import FeedbackStats

FEEDBACK_TYPES = ["improvement", "skill-idea", "command-idea", "bug-report", "pattern"]


class FeedbackManager:
    """Manages Product Forge feedback and learnings."""

    def __init__(self, learnings_dir: Optional[Path] = None):
        """
        Initialize feedback manager.

        Args:
            learnings_dir: Path to learnings directory (default: ~/.claude/learnings)
        """
        self.learnings_dir = learnings_dir or (Path.home() / ".claude" / "learnings")
        self.projects_file = self.learnings_dir / "projects.json"
        self.stats_file = self.learnings_dir / "stats.json"

    def initialize(self, force: bool = False) -> bool:
        """
        Initialize learnings directory structure.

        Args:
            force: Reinitialize even if directory exists

        Returns:
            True if initialized, False if already exists (and force=False)
        """
        if self.learnings_dir.exists() and not force:
            return False

        # Create directory structure
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        (self.learnings_dir / "projects").mkdir(exist_ok=True)
        (self.learnings_dir / "cross-project").mkdir(exist_ok=True)
        (self.learnings_dir / "synced").mkdir(exist_ok=True)

        # Create projects.json if it doesn't exist
        if not self.projects_file.exists() or force:
            self.projects_file.write_text(json.dumps({"version": "1.0", "projects": {}}, indent=2))

        # Create stats.json if it doesn't exist
        if not self.stats_file.exists() or force:
            self.stats_file.write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "total_feedback": 0,
                        "by_type": dict.fromkeys(FEEDBACK_TYPES, 0),
                        "by_project": {},
                        "last_updated": None,
                    },
                    indent=2,
                )
            )

        return True

    def get_git_remote_url(self, cwd: str) -> Optional[str]:
        """
        Extract the git remote URL from a directory.

        Args:
            cwd: Directory to check

        Returns:
            Git remote URL if found, None otherwise
        """
        try:
            result = subprocess.run(
                ["git", "-C", cwd, "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_project_slug(self, cwd: str) -> str:
        """
        Generate a slug for the project based on its path.

        Args:
            cwd: Project directory

        Returns:
            Project slug
        """
        # Use the directory name as the slug
        path = Path(cwd)
        slug = path.name.lower()
        # Sanitize: replace non-alphanumeric with dashes
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug or "unknown-project"

    def register_project(self, cwd: str) -> str:
        """
        Register a project if not already registered.

        Args:
            cwd: Project directory

        Returns:
            Project slug
        """
        slug = self.get_project_slug(cwd)

        # Ensure directory exists
        if not self.projects_file.exists():
            self.initialize()

        projects = json.loads(self.projects_file.read_text())

        if slug not in projects["projects"]:
            projects["projects"][slug] = {
                "path": cwd,
                "repo": self.get_git_remote_url(cwd),
                "registered": datetime.now().isoformat(),
                "feedback_count": 0,
            }
            self.projects_file.write_text(json.dumps(projects, indent=2))

        return slug

    def save_feedback_item(
        self, item: dict[str, Any], project_slug: str, session_id: str, cwd: str
    ) -> Optional[Path]:
        """
        Save a single feedback item to the appropriate directory.

        Args:
            item: Feedback item dict with type, title, description, target
            project_slug: Project identifier
            session_id: Session identifier
            cwd: Current working directory

        Returns:
            Path to saved feedback file, or None if failed
        """
        feedback_type = item.get("type", "improvement")
        if feedback_type not in FEEDBACK_TYPES:
            feedback_type = "improvement"

        title = item.get("title", "Untitled feedback")
        description = item.get("description", "")
        target = item.get("target", "")

        # Create the feedback directory
        feedback_dir = self.learnings_dir / "projects" / project_slug / "feedback" / feedback_type
        feedback_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:30].strip("-")
        filename = f"{date_str}-{title_slug}.md"
        filepath = feedback_dir / filename

        # Get project info
        projects = json.loads(self.projects_file.read_text())
        project_info = projects["projects"].get(project_slug, {})

        # Build the markdown content
        content = f"""---
type: {feedback_type}
status: pending
captured: {datetime.now().isoformat()}
session_id: {session_id}
project: {project_slug}
repo: {project_info.get("repo", "")}
target: {target}
---

# {title}

{description}
"""

        filepath.write_text(content)
        return filepath

    def save_feedback(self, feedback_data: dict[str, Any]) -> int:
        """
        Save feedback from stdin to learnings directory.

        Args:
            feedback_data: Parsed feedback data from hook

        Returns:
            Number of feedback items saved
        """
        # Extract session metadata
        session_id = feedback_data.get("session_id", "unknown")
        cwd = feedback_data.get("cwd", os.getcwd())

        # Extract feedback items
        feedback_items = self._extract_feedback_items(feedback_data)

        if not feedback_items:
            return 0

        # Ensure learnings directory exists
        if not self.learnings_dir.exists():
            self.initialize()

        # Register project
        project_slug = self.register_project(cwd)

        # Save each feedback item
        saved_count = 0
        for item in feedback_items:
            if not isinstance(item, dict):
                continue
            filepath = self.save_feedback_item(item, project_slug, session_id, cwd)
            if filepath:
                saved_count += 1

        # Update statistics
        if saved_count > 0:
            stats = FeedbackStats.load(self.stats_file)
            for item in feedback_items:
                if isinstance(item, dict):
                    feedback_type = item.get("type", "improvement")
                    stats.update(feedback_type, project_slug)
            stats.save(self.stats_file)

            # Update project feedback count
            projects = json.loads(self.projects_file.read_text())
            if project_slug in projects["projects"]:
                projects["projects"][project_slug]["feedback_count"] = stats.by_project.get(
                    project_slug, 0
                )
                self.projects_file.write_text(json.dumps(projects, indent=2))

        return saved_count

    def _extract_feedback_items(self, hook_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract feedback items from the prompt hook's output.

        Args:
            hook_data: Hook data from stdin

        Returns:
            List of feedback items
        """
        # Try direct structure first
        if "feedback" in hook_data:
            return hook_data.get("feedback", [])

        # Try nested in result/output
        for key in ["result", "output", "response"]:
            if key in hook_data and isinstance(hook_data[key], dict):
                if "feedback" in hook_data[key]:
                    return hook_data[key].get("feedback", [])

        # Try to find feedback in string content (prompt hook might return text)
        for key in ["result", "output", "response", "content"]:
            if key in hook_data and isinstance(hook_data[key], str):
                try:
                    parsed = json.loads(hook_data[key])
                    if "feedback" in parsed:
                        return parsed.get("feedback", [])
                except json.JSONDecodeError:
                    # Try to extract JSON from the string
                    match = re.search(r'\{[^{}]*"feedback"[^{}]*\}', hook_data[key])
                    if match:
                        try:
                            parsed = json.loads(match.group())
                            if "feedback" in parsed:
                                return parsed.get("feedback", [])
                        except json.JSONDecodeError:
                            pass

        return []

    def list_feedback(
        self, project: Optional[str] = None, feedback_type: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        List feedback items with optional filters.

        Args:
            project: Filter by project slug
            feedback_type: Filter by feedback type

        Returns:
            List of feedback items with metadata
        """
        feedback_items = []

        projects_dir = self.learnings_dir / "projects"
        if not projects_dir.exists():
            return feedback_items

        # Iterate through projects
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            # Filter by project if specified
            if project and project_dir.name != project:
                continue

            feedback_dir = project_dir / "feedback"
            if not feedback_dir.exists():
                continue

            # Iterate through feedback types
            for type_dir in feedback_dir.iterdir():
                if not type_dir.is_dir():
                    continue

                # Filter by type if specified
                if feedback_type and type_dir.name != feedback_type:
                    continue

                # Iterate through feedback files
                for feedback_file in type_dir.glob("*.md"):
                    try:
                        content = feedback_file.read_text()
                        # Extract frontmatter
                        if content.startswith("---"):
                            parts = content.split("---", 2)
                            if len(parts) >= 3:
                                # Parse YAML-like frontmatter (simple key: value)
                                frontmatter = {}
                                for line in parts[1].strip().split("\n"):
                                    if ":" in line:
                                        key, value = line.split(":", 1)
                                        frontmatter[key.strip()] = value.strip()

                                feedback_items.append(
                                    {
                                        "file": str(feedback_file),
                                        "project": project_dir.name,
                                        "type": type_dir.name,
                                        **frontmatter,
                                    }
                                )
                    except Exception:
                        continue

        return feedback_items
