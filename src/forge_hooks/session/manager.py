"""Core session management operations."""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .stats import SessionStats


class SessionManager:
    """Manages Claude Code session captures."""

    def __init__(self, learnings_dir: Optional[Path] = None):
        """
        Initialize session manager.

        Args:
            learnings_dir: Path to learnings directory (default: ~/.claude/learnings)
        """
        self.learnings_dir = learnings_dir or (Path.home() / ".claude" / "learnings")
        self.sessions_dir = self.learnings_dir / "sessions"
        self.projects_file = self.learnings_dir / "projects.json"
        self.stats_file = self.learnings_dir / "session_stats.json"

    def initialize(self, force: bool = False) -> bool:
        """
        Initialize learnings directory structure for sessions.

        Args:
            force: Reinitialize even if directory exists

        Returns:
            True if initialized, False if already exists (and force=False)
        """
        if self.sessions_dir.exists() and not force:
            return False

        # Create directory structure
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)

        # Create projects.json if it doesn't exist
        if not self.projects_file.exists() or force:
            self.projects_file.write_text(json.dumps({"version": "1.0", "projects": {}}, indent=2))

        # Create session_stats.json if it doesn't exist
        if not self.stats_file.exists() or force:
            self.stats_file.write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "total_sessions": 0,
                        "processed_sessions": 0,
                        "by_project": {},
                        "last_session": None,
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
                "session_count": 0,
            }
            self.projects_file.write_text(json.dumps(projects, indent=2))

        return slug

    def save_session(self, session_data: dict[str, Any]) -> Optional[Path]:
        """
        Save session metadata from stdin to sessions directory.

        Args:
            session_data: Parsed session data from hook

        Returns:
            Path to saved session file, or None if failed
        """
        # Extract session metadata
        session_id = session_data.get("session_id", "unknown")
        cwd = session_data.get("cwd", os.getcwd())
        transcript_path = session_data.get("transcript_path", "")
        captured_at = datetime.now().isoformat()

        # Ensure sessions directory exists
        if not self.sessions_dir.exists():
            self.initialize()

        # Register project
        project_slug = self.register_project(cwd)

        # Get project info
        projects = json.loads(self.projects_file.read_text())
        project_info = projects["projects"].get(project_slug, {})

        # Build session record
        session_record = {
            "session_id": session_id,
            "project": project_slug,
            "cwd": cwd,
            "transcript_path": transcript_path,
            "captured_at": captured_at,
            "processed": False,
            "repo": project_info.get("repo", ""),
        }

        # Generate filename
        date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{date_str}-{project_slug}-{session_id[:8]}.json"
        filepath = self.sessions_dir / filename

        # Save session record
        filepath.write_text(json.dumps(session_record, indent=2))

        # Update statistics
        stats = SessionStats.load(self.stats_file)
        stats.update(project_slug, captured_at)
        stats.save(self.stats_file)

        # Update project session count
        if project_slug in projects["projects"]:
            projects["projects"][project_slug]["session_count"] = stats.by_project.get(
                project_slug, 0
            )
            self.projects_file.write_text(json.dumps(projects, indent=2))

        return filepath

    def list_sessions(
        self, project: Optional[str] = None, processed: Optional[bool] = None
    ) -> list[dict[str, Any]]:
        """
        List sessions with optional filters.

        Args:
            project: Filter by project slug
            processed: Filter by processed status (True/False/None for all)

        Returns:
            List of session records with metadata
        """
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        # Iterate through session files
        for session_file in sorted(self.sessions_dir.glob("*.json"), reverse=True):
            try:
                session_data = json.loads(session_file.read_text())

                # Filter by project if specified
                if project and session_data.get("project") != project:
                    continue

                # Filter by processed status if specified
                if processed is not None and session_data.get("processed", False) != processed:
                    continue

                # Add file path to session data
                session_data["file"] = str(session_file)
                sessions.append(session_data)

            except Exception:
                continue

        return sessions

    def get_session(self, session_file: str) -> Optional[dict[str, Any]]:
        """
        Read a specific session.

        Args:
            session_file: Path to session file

        Returns:
            Session data dict, or None if not found
        """
        filepath = Path(session_file)
        if not filepath.exists():
            return None

        try:
            return json.loads(filepath.read_text())
        except Exception:
            return None

    def mark_processed(self, session_file: str) -> bool:
        """
        Mark session as processed after LLM analysis.

        Args:
            session_file: Path to session file

        Returns:
            True if successful, False otherwise
        """
        filepath = Path(session_file)
        if not filepath.exists():
            return False

        try:
            session_data = json.loads(filepath.read_text())
            session_data["processed"] = True
            session_data["processed_at"] = datetime.now().isoformat()
            filepath.write_text(json.dumps(session_data, indent=2))

            # Update statistics
            stats = SessionStats.load(self.stats_file)
            stats.mark_processed()
            stats.save(self.stats_file)

            return True
        except Exception:
            return False
