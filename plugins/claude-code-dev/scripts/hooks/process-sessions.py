#!/usr/bin/env python3
"""
Product Forge Session Processor

Processes captured sessions with LLM analysis to extract feedback.
Called by /sync-feedback command.

Usage:
    python3 process-sessions.py [--all] [--project <slug>] [--dry-run]
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List


# === CONFIGURATION ===

LEARNINGS_DIR = Path.home() / ".claude" / "learnings"
SESSIONS_DIR = LEARNINGS_DIR / "sessions"
PROJECTS_FILE = LEARNINGS_DIR / "projects.json"
STATS_FILE = LEARNINGS_DIR / "stats.json"

FEEDBACK_TYPES = ["improvement", "skill-idea", "command-idea", "bug-report", "pattern"]


# === UTILITY FUNCTIONS ===

def log(msg: str) -> None:
    """Log message to stderr."""
    print(f"[process-sessions] {msg}", file=sys.stderr)


def ensure_dirs() -> None:
    """Initialize directory structure."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if not STATS_FILE.exists():
        STATS_FILE.write_text(json.dumps({
            "version": "1.0",
            "total_feedback": 0,
            "by_type": {t: 0 for t in FEEDBACK_TYPES},
            "by_project": {},
            "last_updated": datetime.now().isoformat()
        }, indent=2))


def get_pending_sessions(project_filter: Optional[str] = None) -> List[Path]:
    """Get list of unprocessed session files."""
    sessions = []
    for f in SESSIONS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if data.get("processed"):
                continue
            if project_filter and data.get("project") != project_filter:
                continue
            sessions.append(f)
        except (json.JSONDecodeError, IOError):
            continue
    return sorted(sessions)


def read_transcript(transcript_path: str) -> List[dict]:
    """Read transcript JSONL file."""
    entries = []
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        log(f"Failed to read transcript: {e}")
    return entries


def extract_user_messages(entries: List[dict]) -> str:
    """Extract user messages from transcript entries."""
    messages = []
    for entry in entries:
        if entry.get("type") != "user":
            continue

        message = entry.get("message", {})
        content = ""

        if isinstance(message, dict):
            content = message.get("content", "")
        elif isinstance(message, str):
            content = message

        if not content or not isinstance(content, str):
            continue

        # Skip system/meta messages
        if content.startswith("<") and content.endswith(">"):
            continue
        if "<local-command" in content or "<command-name>" in content:
            continue

        content = content.strip()
        if len(content) > 10:
            messages.append(content[:1000])

    return "\n---\n".join(messages[-50:])


def load_prompt_template() -> str:
    """Load the analysis prompt template."""
    script_dir = Path(__file__).parent
    prompt_file = script_dir / "prompts" / "analyze-session.txt"

    if prompt_file.exists():
        return prompt_file.read_text()

    # Fallback inline prompt (braces doubled for str.format compatibility)
    return '''Analyze these user messages from a Claude Code session. Identify actionable feedback.

USER MESSAGES:
"""
{messages}
"""

Respond with JSON: {{"feedback": [{{"type": "improvement|skill-idea|command-idea|bug-report|pattern", "title": "...", "description": "...", "target": "..."}}]}}
If none found: {{"feedback": []}}'''


def analyze_with_claude(user_messages: str) -> List[dict]:
    """Use claude -p to analyze user messages for feedback."""
    if not user_messages or len(user_messages) < 50:
        return []

    template = load_prompt_template()
    prompt = template.format(messages=user_messages[:15000])

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            log(f"claude -p failed: {result.stderr[:200]}")
            return []

        output = result.stdout.strip()

        # Parse response (claude wraps in {"result": "..."})
        data = None
        try:
            wrapper = json.loads(output)
            if "result" in wrapper:
                inner = wrapper["result"]
                # Strip markdown code fences (handles both actual and escaped newlines)
                inner = re.sub(r'^```(?:json)?[\s\\n]*', '', inner)
                inner = re.sub(r'[\s\\n]*```$', '', inner)
                inner = inner.strip()
                data = json.loads(inner)
            elif "feedback" in wrapper:
                data = wrapper
        except json.JSONDecodeError as e:
            log(f"JSON parse error: {e}, inner={inner[:100] if 'inner' in dir() else 'N/A'}")
            pass

        if data:
            feedback = data.get("feedback", [])
            if isinstance(feedback, list):
                return feedback[:10]
        return []

    except subprocess.TimeoutExpired:
        log("claude -p timed out")
        return []
    except FileNotFoundError:
        log("claude CLI not found")
        return []
    except Exception as e:
        log(f"LLM analysis error: {e}")
        return []


def save_feedback_item(
    item: dict,
    project_slug: str,
    session_id: str
) -> Optional[Path]:
    """Save a single feedback item."""
    feedback_type = item.get("type", "improvement")
    if feedback_type not in FEEDBACK_TYPES:
        feedback_type = "improvement"

    title = item.get("title", "Untitled feedback")
    description = item.get("description", "")
    target = item.get("target", "")

    feedback_dir = LEARNINGS_DIR / "projects" / project_slug / "feedback" / feedback_type
    feedback_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:30].strip("-")
    filename = f"{date_str}-{title_slug}.md"
    filepath = feedback_dir / filename

    # Get project info
    projects = json.loads(PROJECTS_FILE.read_text()) if PROJECTS_FILE.exists() else {"projects": {}}
    project_info = projects.get("projects", {}).get(project_slug, {})

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
    return filepath


def update_stats(project_slug: str, feedback_items: List[dict]) -> None:
    """Update global statistics."""
    stats = json.loads(STATS_FILE.read_text()) if STATS_FILE.exists() else {
        "total_feedback": 0,
        "by_type": {t: 0 for t in FEEDBACK_TYPES},
        "by_project": {}
    }

    for item in feedback_items:
        feedback_type = item.get("type", "improvement")
        if feedback_type in FEEDBACK_TYPES:
            stats["total_feedback"] += 1
            stats["by_type"][feedback_type] = stats["by_type"].get(feedback_type, 0) + 1
            stats["by_project"][project_slug] = stats["by_project"].get(project_slug, 0) + 1

    stats["last_updated"] = datetime.now().isoformat()
    STATS_FILE.write_text(json.dumps(stats, indent=2))


def process_session(session_file: Path, dry_run: bool = False) -> int:
    """Process a single session file. Returns number of feedback items."""
    try:
        session_data = json.loads(session_file.read_text())
    except (json.JSONDecodeError, IOError) as e:
        log(f"Failed to read session file: {e}")
        return 0

    transcript_path = session_data.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        log(f"Transcript not found: {transcript_path}")
        return 0

    project_slug = session_data.get("project", "unknown")
    session_id = session_data.get("session_id", "unknown")

    log(f"Processing session {session_id[:8]} for project '{project_slug}'")

    # Read and analyze transcript
    entries = read_transcript(transcript_path)
    if not entries:
        log("No transcript entries")
        return 0

    user_messages = extract_user_messages(entries)
    if not user_messages:
        log("No user messages to analyze")
        return 0

    if dry_run:
        log(f"[dry-run] Would analyze {len(user_messages)} chars of messages")
        return 0

    # Analyze with LLM
    feedback_items = analyze_with_claude(user_messages)

    if not feedback_items:
        log("No feedback found")
        # Mark as processed even if no feedback
        session_data["processed"] = True
        session_data["processed_at"] = datetime.now().isoformat()
        session_data["feedback_count"] = 0
        session_file.write_text(json.dumps(session_data, indent=2))
        return 0

    # Save feedback items
    saved_count = 0
    for item in feedback_items:
        if not isinstance(item, dict):
            continue
        filepath = save_feedback_item(item, project_slug, session_id)
        if filepath:
            saved_count += 1
            log(f"  Saved: {filepath.name}")

    # Update stats
    if saved_count > 0:
        update_stats(project_slug, feedback_items)

    # Mark session as processed
    session_data["processed"] = True
    session_data["processed_at"] = datetime.now().isoformat()
    session_data["feedback_count"] = saved_count
    session_file.write_text(json.dumps(session_data, indent=2))

    return saved_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Process captured sessions with LLM analysis")
    parser.add_argument("--all", action="store_true", help="Process all pending sessions")
    parser.add_argument("--project", type=str, help="Only process sessions for this project")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--status", action="store_true", help="Show pending session count")
    args = parser.parse_args()

    ensure_dirs()

    pending = get_pending_sessions(args.project)

    if args.status:
        print(f"Pending sessions: {len(pending)}")
        for f in pending[:10]:
            data = json.loads(f.read_text())
            print(f"  - {data.get('project')}: {data.get('session_id', '')[:8]} ({f.name})")
        if len(pending) > 10:
            print(f"  ... and {len(pending) - 10} more")
        return 0

    if not pending:
        print("No pending sessions to process")
        return 0

    if not args.all and len(pending) > 1:
        print(f"Found {len(pending)} pending sessions. Use --all to process all, or specify --project")
        return 0

    total_feedback = 0
    for session_file in pending:
        count = process_session(session_file, args.dry_run)
        total_feedback += count

    print(f"\nProcessed {len(pending)} sessions, found {total_feedback} feedback items")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        import traceback
        log(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)
