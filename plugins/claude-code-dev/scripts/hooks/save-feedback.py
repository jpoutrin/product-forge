#!/usr/bin/env python3
"""
Product Forge Session Capture Hook

Captures session metadata on Stop for later LLM analysis.
This script runs quickly without LLM calls.

Use /sync-feedback to process captured sessions with LLM analysis.

Input (via stdin): JSON with session metadata from Claude Code
Output: Saves session record to ~/.claude/learnings/sessions/
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# === CONFIGURATION ===

LEARNINGS_DIR = Path.home() / ".claude" / "learnings"
SESSIONS_DIR = LEARNINGS_DIR / "sessions"
PROJECTS_FILE = LEARNINGS_DIR / "projects.json"


# === UTILITY FUNCTIONS ===

def log(msg: str) -> None:
    """Log message to stderr (visible in verbose mode)."""
    print(f"[session-capture] {msg}", file=sys.stderr)


def ensure_dirs() -> None:
    """Initialize directory structure."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if not PROJECTS_FILE.exists():
        PROJECTS_FILE.write_text(json.dumps({
            "version": "1.0",
            "projects": {}
        }, indent=2))


def get_git_remote_url(cwd: str) -> Optional[str]:
    """Extract the git remote URL from a directory."""
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_project_slug(cwd: str) -> str:
    """Generate a slug for the project based on its path."""
    path = Path(cwd)
    slug = path.name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "unknown-project"


def register_project(cwd: str) -> str:
    """Register a project if not already registered. Returns the project slug."""
    slug = get_project_slug(cwd)

    projects = json.loads(PROJECTS_FILE.read_text())

    if slug not in projects["projects"]:
        log(f"Registering new project: {slug}")
        projects["projects"][slug] = {
            "path": cwd,
            "repo": get_git_remote_url(cwd),
            "registered": datetime.now().isoformat(),
            "session_count": 0
        }
        PROJECTS_FILE.write_text(json.dumps(projects, indent=2))

    return slug


def parse_hook_input() -> dict:
    """Parse the JSON input from stdin."""
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return {}
        return json.loads(raw_input)
    except json.JSONDecodeError as e:
        log(f"Failed to parse input JSON: {e}")
        return {}


def save_session(hook_data: dict) -> Optional[Path]:
    """Save session metadata for later processing."""
    session_id = hook_data.get("session_id", "unknown")
    cwd = hook_data.get("cwd", os.getcwd())
    transcript_path = hook_data.get("transcript_path", "")

    if not transcript_path or not Path(transcript_path).exists():
        log("No valid transcript path")
        return None

    project_slug = register_project(cwd)

    # Create session record
    session_record = {
        "session_id": session_id,
        "project": project_slug,
        "cwd": cwd,
        "transcript_path": transcript_path,
        "captured_at": datetime.now().isoformat(),
        "processed": False
    }

    # Save to sessions directory
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    session_file = SESSIONS_DIR / f"{date_str}-{session_id[:8]}.json"
    session_file.write_text(json.dumps(session_record, indent=2))

    # Update project session count
    projects = json.loads(PROJECTS_FILE.read_text())
    if project_slug in projects["projects"]:
        projects["projects"][project_slug]["session_count"] = \
            projects["projects"][project_slug].get("session_count", 0) + 1
        projects["projects"][project_slug]["last_session"] = datetime.now().isoformat()
        PROJECTS_FILE.write_text(json.dumps(projects, indent=2))

    return session_file


def main() -> int:
    """Main entry point."""
    hook_data = parse_hook_input()

    if not hook_data:
        log("No input received, exiting")
        return 0

    if hook_data.get("stop_hook_active"):
        log("Stop hook already active, skipping")
        return 0

    ensure_dirs()

    session_file = save_session(hook_data)

    if session_file:
        log(f"Session captured: {session_file.name}")
    else:
        log("No session captured")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)
