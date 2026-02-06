#!/usr/bin/env python3
"""
Product Forge Feedback Save Hook

Receives feedback from the Stop hook's prompt analysis and saves it to
~/.claude/learnings/ for later review and sync to Product Forge.

This script is called by a command hook after the prompt hook analyzes
the session for improvement opportunities.

Input (via stdin): JSON with prompt hook output + session metadata
Output: Saves feedback files to ~/.claude/learnings/projects/{slug}/feedback/
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
PROJECTS_FILE = LEARNINGS_DIR / "projects.json"
STATS_FILE = LEARNINGS_DIR / "stats.json"

FEEDBACK_TYPES = ["improvement", "skill-idea", "command-idea", "bug-report", "pattern"]


# === UTILITY FUNCTIONS ===

def log(msg: str) -> None:
    """Log message to stderr (visible in verbose mode)."""
    print(f"[feedback-hook] {msg}", file=sys.stderr)


def ensure_learnings_dir() -> None:
    """Initialize the learnings directory structure if it doesn't exist."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)

    if not PROJECTS_FILE.exists():
        PROJECTS_FILE.write_text(json.dumps({
            "version": "1.0",
            "projects": {}
        }, indent=2))

    if not STATS_FILE.exists():
        STATS_FILE.write_text(json.dumps({
            "version": "1.0",
            "total_feedback": 0,
            "by_type": {t: 0 for t in FEEDBACK_TYPES},
            "by_project": {},
            "last_updated": datetime.now().isoformat()
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
    # Use the directory name as the slug
    path = Path(cwd)
    slug = path.name.lower()
    # Sanitize: replace non-alphanumeric with dashes
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
            "feedback_count": 0
        }
        PROJECTS_FILE.write_text(json.dumps(projects, indent=2))

    return slug


def save_feedback_item(
    item: dict,
    project_slug: str,
    session_id: str,
    cwd: str
) -> Optional[Path]:
    """Save a single feedback item to the appropriate directory."""
    feedback_type = item.get("type", "improvement")
    if feedback_type not in FEEDBACK_TYPES:
        log(f"Unknown feedback type: {feedback_type}, using 'improvement'")
        feedback_type = "improvement"

    title = item.get("title", "Untitled feedback")
    description = item.get("description", "")
    target = item.get("target", "")

    # Create the feedback directory
    feedback_dir = LEARNINGS_DIR / "projects" / project_slug / "feedback" / feedback_type
    feedback_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:30].strip("-")
    filename = f"{date_str}-{title_slug}.md"
    filepath = feedback_dir / filename

    # Get project info
    projects = json.loads(PROJECTS_FILE.read_text())
    project_info = projects["projects"].get(project_slug, {})

    # Build the markdown content
    content = f"""---
type: {feedback_type}
status: pending
captured: {datetime.now().isoformat()}
session_id: {session_id}
project: {project_slug}
repo: {project_info.get('repo', '')}
target: {target}
---

# {title}

{description}
"""

    filepath.write_text(content)
    log(f"Saved feedback: {filepath}")
    return filepath


def update_stats(project_slug: str, feedback_items: list) -> None:
    """Update the global statistics."""
    stats = json.loads(STATS_FILE.read_text())
    projects = json.loads(PROJECTS_FILE.read_text())

    for item in feedback_items:
        feedback_type = item.get("type", "improvement")
        if feedback_type in FEEDBACK_TYPES:
            stats["total_feedback"] += 1
            stats["by_type"][feedback_type] = stats["by_type"].get(feedback_type, 0) + 1
            stats["by_project"][project_slug] = stats["by_project"].get(project_slug, 0) + 1

    stats["last_updated"] = datetime.now().isoformat()
    STATS_FILE.write_text(json.dumps(stats, indent=2))

    # Update project feedback count
    if project_slug in projects["projects"]:
        projects["projects"][project_slug]["feedback_count"] = stats["by_project"].get(project_slug, 0)
        PROJECTS_FILE.write_text(json.dumps(projects, indent=2))


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


def extract_feedback_from_prompt_output(hook_data: dict) -> list:
    """
    Extract feedback items from the prompt hook's output.

    The prompt hook outputs JSON like:
    {"feedback": [{"type": "...", "title": "...", "description": "...", "target": "..."}]}

    This might be in hook_data directly or in a 'result' or 'output' field.
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


def main() -> int:
    """Main entry point."""
    # Parse input
    hook_data = parse_hook_input()

    if not hook_data:
        log("No input received, exiting")
        return 0

    # Check for stop_hook_active to prevent loops
    if hook_data.get("stop_hook_active"):
        log("Stop hook already active, skipping to prevent loop")
        return 0

    # Extract session metadata
    session_id = hook_data.get("session_id", "unknown")
    cwd = hook_data.get("cwd", os.getcwd())

    # Extract feedback items
    feedback_items = extract_feedback_from_prompt_output(hook_data)

    if not feedback_items:
        log("No feedback items found in session")
        return 0

    log(f"Found {len(feedback_items)} feedback items")

    # Ensure learnings directory exists
    ensure_learnings_dir()

    # Register project
    project_slug = register_project(cwd)

    # Save each feedback item
    saved_files = []
    for item in feedback_items:
        if not isinstance(item, dict):
            continue
        filepath = save_feedback_item(item, project_slug, session_id, cwd)
        if filepath:
            saved_files.append(filepath)

    # Update statistics
    if saved_files:
        update_stats(project_slug, feedback_items)
        log(f"Saved {len(saved_files)} feedback items for project '{project_slug}'")

    return 0


if __name__ == "__main__":
    # Deprecation notice
    print("⚠️  DEPRECATED: Use 'forge feedback save' instead", file=sys.stderr)
    print("See: forge feedback --help", file=sys.stderr)
    print("", file=sys.stderr)

    try:
        sys.exit(main())
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)
