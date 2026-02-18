"""CLI interface for Product Forge."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click

from .common.hook_io import output_result
from .common.logging_config import (
    log_hook_execution,
    log_validation,
    setup_logging,
)
from .validators import FileContainsValidator, FileOwnershipValidator, NewFileValidator

# Setup logging (file-based with rotation)
# Skip logging setup if we're just viewing logs (to avoid polluting the output)
_skip_logging = len(sys.argv) > 1 and sys.argv[1] == "logs"
if not _skip_logging:
    log_level = os.environ.get("FORGE_LOG_LEVEL", "INFO")
    logger = setup_logging(log_level=log_level)
else:
    # Create a dummy logger that doesn't log anything
    import logging

    logger = logging.getLogger("forge_hooks")
    logger.addHandler(logging.NullHandler())


@click.group()
@click.version_option(version="0.2.0", prog_name="forge")
def main():
    """Product Forge command-line tools and utilities."""
    pass


@main.command("logs")
@click.option(
    "-n",
    "--lines",
    type=int,
    default=None,
    help="Number of lines to show (default: 10, or all with -f)",
)
@click.option("-f", "--follow", is_flag=True, help="Follow log file (like tail -f)")
@click.option(
    "--file",
    "log_file",
    default=None,
    help="Specific log file to view (default: forge-cli.log)",
)
def logs_command(lines: Optional[int], follow: bool, log_file: Optional[str]) -> None:
    """
    View forge-cli log files.

    This command provides a convenient way to tail the forge-cli logs
    without needing to remember the log file location.

    Examples:

      forge logs              # Show last 10 lines

      forge logs -n 50        # Show last 50 lines

      forge logs -f           # Follow logs in real-time

      forge logs -f -n 100    # Follow with 100 initial lines
    """
    import subprocess

    from .common.logging_config import get_log_directory

    # Get log file path
    log_dir = get_log_directory()
    if log_file is None:
        log_file = "forge-cli.log"
    log_path = log_dir / log_file

    # Check if log file exists
    if not log_path.exists():
        click.echo(f"Log file not found: {log_path}", err=True)
        click.echo(f"\nLog directory: {log_dir}", err=True)
        click.echo("\nAvailable log files:", err=True)
        if log_dir.exists():
            log_files = sorted(log_dir.glob("*.log*"))
            if log_files:
                for f in log_files:
                    click.echo(f"  - {f.name}", err=True)
            else:
                click.echo("  (none)", err=True)
        sys.exit(1)

    # Build tail command
    cmd = ["tail"]

    # Add follow flag if requested
    if follow:
        cmd.append("-f")

    # Add lines option
    if lines is not None:
        cmd.extend(["-n", str(lines)])
    elif not follow:
        # Default to 10 lines if not following
        cmd.extend(["-n", "10"])

    # Add log file path
    cmd.append(str(log_path))

    # Execute tail command
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C (when following)
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error running tail: {e}", err=True)
        sys.exit(1)


@main.group()
def validate():
    """File validation commands."""
    pass


@validate.command(name="new-file")
@click.option(
    "-d", "--directory", default="specs", help="Directory to check for new files (default: specs)"
)
@click.option("-e", "--extension", default=".md", help="File extension to match (default: .md)")
@click.option("--max-age", default=5, type=int, help="Maximum file age in minutes (default: 5)")
def validate_new_file(directory: str, extension: str, max_age: int):
    """
    Validate that a new file was created.

    Checks git status for untracked/new files and file modification times
    to verify a new file matching the pattern was created.
    """
    logger.info(f"Running new-file validation: dir={directory}, ext={extension}, max_age={max_age}")

    validator = NewFileValidator(directory, extension, max_age)
    result = validator.validate()

    # Log validation result
    log_validation(
        validator="new-file",
        passed=result.ok,
        reason=result.message if not result.ok else None,
    )

    output_result(result)
    sys.exit(result.exit_code)


@validate.command(name="contains")
@click.option(
    "-d", "--directory", default="specs", help="Directory to check for files (default: specs)"
)
@click.option("-e", "--extension", default=".md", help="File extension to match (default: .md)")
@click.option(
    "--contains",
    multiple=True,
    required=True,
    help="Required string that must be in the file (can be used multiple times)",
)
@click.option("--max-age", default=5, type=int, help="Maximum file age in minutes (default: 5)")
def validate_contains(directory: str, extension: str, contains: tuple, max_age: int):
    """
    Validate that a file contains required content.

    Finds the newest file in the directory and checks that it contains
    all specified strings (case-sensitive).
    """
    logger.info(
        f"Running contains validation: dir={directory}, ext={extension}, "
        f"requires={list(contains)}, max_age={max_age}"
    )

    validator = FileContainsValidator(directory, extension, list(contains), max_age)
    result = validator.validate()

    # Log validation result
    log_validation(
        validator="contains",
        passed=result.ok,
        reason=result.message if not result.ok else None,
    )

    output_result(result)
    sys.exit(result.exit_code)


@validate.command(name="ownership")
@click.option(
    "-d", "--directory", default="specs", help="Directory to check for plan files (default: specs)"
)
@click.option("-e", "--extension", default=".md", help="File extension to match (default: .md)")
@click.option("--max-age", default=5, type=int, help="Maximum file age in minutes (default: 5)")
def validate_ownership(directory: str, extension: str, max_age: int):
    """
    Validate file ownership rules in task orchestration plans.

    Checks:
    1. Each file is CREATEd by at most one task
    2. Parallel tasks (same wave) with unscoped MODIFY target different files
    3. Parallel tasks with scoped MODIFY have non-overlapping scopes
    4. No task modifies files in its BOUNDARY list
    """
    logger.info(
        f"Running ownership validation: dir={directory}, ext={extension}, max_age={max_age}"
    )

    validator = FileOwnershipValidator(directory, extension, max_age)
    result = validator.validate()

    # Log validation result
    log_validation(
        validator="ownership",
        passed=result.ok,
        reason=result.message if not result.ok else None,
    )

    output_result(result)
    sys.exit(result.exit_code)


@validate.command(name="django")
@click.option(
    "-f",
    "--files",
    default=None,
    help="Files or directory to validate (default: current directory)",
)
@click.option("--skip-mypy", is_flag=True, help="Skip type checking")
@click.option("--skip-ruff", is_flag=True, help="Skip linting")
@click.option("--skip-tests", is_flag=True, help="Skip unit tests")
@click.option("--skip-django-checks", is_flag=True, help="Skip Django system checks")
@click.option(
    "--coverage",
    type=int,
    default=80,
    help="Minimum coverage percentage (default: 80)",
)
def validate_django(
    files: Optional[str],
    skip_mypy: bool,
    skip_ruff: bool,
    skip_tests: bool,
    skip_django_checks: bool,
    coverage: int,
):
    """
    Validate Django projects with comprehensive checks.

    Runs type checking, linting, tests, and Django-specific validations.

    Examples:

      forge validate django

      forge validate django --files app/models.py

      forge validate django --skip-tests

      forge validate django --coverage 90
    """
    from .validators import DjangoValidator

    logger.info(f"Running Django validation: files={files or '.'}")

    validator = DjangoValidator(
        files=files,
        skip_mypy=skip_mypy,
        skip_ruff=skip_ruff,
        skip_tests=skip_tests,
        skip_django_checks=skip_django_checks,
        coverage_threshold=coverage,
    )
    result = validator.validate()

    # Log validation result
    log_validation(
        validator="django",
        passed=result.ok,
        reason=result.message if not result.ok else None,
    )

    output_result(result)
    sys.exit(result.exit_code)


@validate.command(name="ruff")
@click.option(
    "-f",
    "--files",
    default=None,
    help="Files or directory to validate (default: current directory)",
)
@click.option("--fix", is_flag=True, help="Automatically fix issues when possible")
def validate_ruff(files: Optional[str], fix: bool):
    """
    Validate Python code with ruff linting.

    Runs code style enforcement, PEP 8 compliance checks, and common bug pattern detection.

    Examples:

      forge validate ruff

      forge validate ruff --files src/

      forge validate ruff --fix
    """
    from .validators import RuffValidator

    logger.info(f"Running ruff validation: files={files or '.'}, fix={fix}")

    validator = RuffValidator(files=files, fix=fix)
    result = validator.validate()

    # Log validation result
    log_validation(
        validator="ruff",
        passed=result.ok,
        reason=result.message if not result.ok else None,
    )

    output_result(result)
    sys.exit(result.exit_code)


@validate.command(name="ty")
@click.option(
    "-f",
    "--files",
    default=None,
    help="Files or directory to validate (default: current directory)",
)
@click.option("--strict", is_flag=True, help="Use strict type checking mode")
def validate_type(files: Optional[str], strict: bool):
    """
    Validate Python code with mypy type checking.

    Checks Python type hints and ensures type safety across your codebase.

    Examples:

      forge validate ty

      forge validate ty --files src/

      forge validate ty --strict
    """
    from .validators import TypeValidator

    logger.info(f"Running type validation: files={files or '.'}, strict={strict}")

    validator = TypeValidator(files=files, strict=strict)
    result = validator.validate()

    # Log validation result
    log_validation(
        validator="type",
        passed=result.ok,
        reason=result.message if not result.ok else None,
    )

    output_result(result)
    sys.exit(result.exit_code)


# === YOUTUBE COMMAND ===


@main.command("youtube")
@click.argument("url")
@click.option(
    "--output", "-o", type=click.Path(), default=".work/transcripts", help="Output directory"
)
def youtube(url: str, output: str) -> None:
    """
    Fetch YouTube video transcript.

    Saves transcript as readable text file in output directory.
    Supports various YouTube URL formats and direct video IDs.

    Examples:

      forge youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

      forge youtube "https://youtu.be/dQw4w9WgXcQ" --output transcripts/

      forge youtube dQw4w9WgXcQ
    """
    from .utils.youtube import YouTubeFetcher

    logger.info(f"Fetching YouTube transcript: url={url}, output={output}")

    fetcher = YouTubeFetcher()

    # Check dependency
    if not fetcher.check_dependency():
        fetcher.print_install_instructions()
        logger.error("YouTube dependency not installed")
        sys.exit(1)

    # Extract video ID
    video_id = fetcher.extract_video_id(url)
    if not video_id:
        click.echo(f"Error: Could not extract video ID from: {url}", err=True)
        click.echo("\nSupported formats:", err=True)
        click.echo("  - https://www.youtube.com/watch?v=VIDEO_ID", err=True)
        click.echo("  - https://youtu.be/VIDEO_ID", err=True)
        click.echo("  - VIDEO_ID (11 characters)", err=True)
        logger.error(f"Invalid YouTube URL: {url}")
        sys.exit(1)

    click.echo(f"Fetching transcript for video: {video_id}", err=True)

    # Fetch and save transcript
    try:
        output_path = fetcher.save_transcript(url, Path(output))
        click.echo(f"Success! Transcript saved to: {output_path}", err=True)
        logger.info(f"YouTube transcript saved: {output_path}")
        log_hook_execution(
            hook_type="youtube",
            operation="fetch-transcript",
            success=True,
            details={"video_id": video_id, "output": str(output_path)},
        )
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Failed to fetch YouTube transcript: {e}")
        log_hook_execution(
            hook_type="youtube",
            operation="fetch-transcript",
            success=False,
            details={"video_id": video_id, "error": str(e)},
        )
        sys.exit(1)


# === FEEDBACK COMMANDS ===


@main.group("feedback")
def feedback():
    """Manage Product Forge feedback and learnings."""
    pass


@feedback.command("init")
@click.option("--force", is_flag=True, help="Reinitialize if exists")
def feedback_init(force: bool) -> None:
    """Initialize learnings directory structure."""
    from .feedback import FeedbackManager

    manager = FeedbackManager()

    if manager.initialize(force=force):
        click.echo(f"Learnings directory initialized at {manager.learnings_dir}")
        click.echo("")
        click.echo("Directory structure:")
        click.echo(f"  {manager.learnings_dir}/")
        click.echo("  ├── projects.json       # Registry of opted-in projects")
        click.echo("  ├── stats.json          # Global feedback statistics")
        click.echo("  ├── projects/           # Per-project feedback")
        click.echo("  │   └── {project-slug}/")
        click.echo("  │       └── feedback/")
        click.echo("  │           ├── improvement/")
        click.echo("  │           ├── skill-idea/")
        click.echo("  │           ├── command-idea/")
        click.echo("  │           ├── bug-report/")
        click.echo("  │           └── pattern/")
        click.echo("  ├── cross-project/      # Cross-project patterns")
        click.echo("  └── synced/             # Archived after sync")
    else:
        click.echo(f"Learnings directory already exists at {manager.learnings_dir}")
        click.echo("Use --force to reinitialize")


@feedback.command("save")
def feedback_save() -> None:
    """Save feedback from stdin (used by hooks)."""
    from .feedback import FeedbackManager

    manager = FeedbackManager()

    # Parse input from stdin
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            click.echo("No input received", err=True)
            logger.warning("Feedback save called with no input")
            sys.exit(0)
        feedback_data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        click.echo(f"Failed to parse input JSON: {e}", err=True)
        logger.error(f"Invalid JSON in feedback input: {e}")
        sys.exit(1)

    # Check for stop_hook_active to prevent loops
    if feedback_data.get("stop_hook_active"):
        click.echo("Stop hook already active, skipping to prevent loop", err=True)
        logger.warning("Feedback save skipped: stop_hook_active=true")
        sys.exit(0)

    # Save feedback
    logger.info("Saving feedback from hook")
    saved_count = manager.save_feedback(feedback_data)

    if saved_count > 0:
        click.echo(f"Saved {saved_count} feedback items", err=True)
        logger.info(f"Saved {saved_count} feedback items")
        log_hook_execution(
            hook_type="feedback",
            operation="save",
            success=True,
            details={"count": saved_count},
        )
    else:
        click.echo("No feedback items found in session", err=True)
        logger.info("No feedback items found in session")


@feedback.command("list")
@click.option("--project", help="Filter by project slug")
@click.option("--type", "feedback_type", help="Filter by feedback type")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def feedback_list(project: Optional[str], feedback_type: Optional[str], output_format: str) -> None:
    """List feedback items."""
    from .feedback import FeedbackManager

    manager = FeedbackManager()
    items = manager.list_feedback(project=project, feedback_type=feedback_type)

    if output_format == "json":
        click.echo(json.dumps(items, indent=2))
    else:
        if not items:
            click.echo("No feedback items found")
            return

        click.echo(f"Found {len(items)} feedback items:\n")
        for item in items:
            click.echo(f"  [{item['type']}] {item.get('title', 'Untitled')}")
            click.echo(f"    Project: {item['project']}")
            click.echo(f"    Status: {item.get('status', 'unknown')}")
            click.echo(f"    Captured: {item.get('captured', 'unknown')}")
            click.echo(f"    File: {item['file']}")
            click.echo("")


@feedback.command("stats")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def feedback_stats(output_format: str) -> None:
    """Show feedback statistics."""
    from .feedback import FeedbackStats

    learnings_dir = Path.home() / ".claude" / "learnings"
    stats_file = learnings_dir / "stats.json"

    stats = FeedbackStats.load(stats_file)

    if output_format == "json":
        click.echo(
            json.dumps(
                {
                    "total": stats.total,
                    "by_type": stats.by_type,
                    "by_project": stats.by_project,
                    "last_updated": stats.last_updated,
                },
                indent=2,
            )
        )
    else:
        click.echo("Feedback Statistics")
        click.echo("=" * 40)
        click.echo(f"Total feedback items: {stats.total}")
        click.echo(f"Last updated: {stats.last_updated}")
        click.echo("")
        click.echo("By Type:")
        for feedback_type, count in stats.by_type.items():
            click.echo(f"  {feedback_type}: {count}")
        click.echo("")
        click.echo("By Project:")
        for project, count in stats.by_project.items():
            click.echo(f"  {project}: {count}")


@feedback.command("sync")
@click.option("--project", help="Sync specific project only")
def feedback_sync(project: Optional[str]) -> None:
    """Sync feedback to Product Forge (placeholder)."""
    click.echo("Sync functionality coming soon...")
    click.echo("This will sync feedback items to Product Forge for review and integration.")


# === SESSION COMMANDS ===


@main.group("session")
def session():
    """Manage Claude Code session captures."""
    pass


@session.command("save")
def session_save() -> None:
    """Save session from stdin (used by hooks)."""
    from .session import SessionManager

    manager = SessionManager()

    # Parse input from stdin
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            click.echo("No input received", err=True)
            logger.warning("Session save called with no input")
            sys.exit(0)
        session_data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        click.echo(f"Failed to parse input JSON: {e}", err=True)
        logger.error(f"Invalid JSON in session input: {e}")
        sys.exit(1)

    # Check for stop_hook_active to prevent loops
    if session_data.get("stop_hook_active"):
        click.echo("Stop hook already active, skipping to prevent loop", err=True)
        logger.warning("Session save skipped: stop_hook_active=true")
        sys.exit(0)

    # Save session
    logger.info("Saving session from hook")
    filepath = manager.save_session(session_data)

    if filepath:
        click.echo(f"Session saved: {filepath.name}", err=True)
        logger.info(f"Session saved: {filepath}")
        log_hook_execution(
            hook_type="session",
            operation="save",
            success=True,
            details={"file": str(filepath)},
        )
    else:
        click.echo("Failed to save session", err=True)
        logger.error("Failed to save session")
        sys.exit(1)


@session.command("list")
@click.option("--project", help="Filter by project slug")
@click.option("--processed/--unprocessed", default=None, help="Filter by processed status")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def session_list(project: Optional[str], processed: Optional[bool], output_format: str) -> None:
    """List captured sessions."""
    from .session import SessionManager

    manager = SessionManager()
    sessions = manager.list_sessions(project=project, processed=processed)

    if output_format == "json":
        click.echo(json.dumps(sessions, indent=2))
    else:
        if not sessions:
            click.echo("No sessions found")
            return

        click.echo(f"Found {len(sessions)} sessions:\n")
        for session in sessions:
            click.echo(f"  [{session['project']}] {session['session_id'][:8]}")
            click.echo(f"    Captured: {session.get('captured_at', 'unknown')}")
            click.echo(f"    Processed: {'Yes' if session.get('processed') else 'No'}")
            if session.get("transcript_path"):
                click.echo(f"    Transcript: {session['transcript_path']}")
            click.echo(f"    File: {session['file']}")
            click.echo("")


@session.command("view")
@click.argument("session_file")
def session_view(session_file: str) -> None:
    """View session details."""
    from .session import SessionManager

    manager = SessionManager()
    session = manager.get_session(session_file)

    if not session:
        click.echo(f"Session not found: {session_file}", err=True)
        sys.exit(1)

    click.echo("Session Details")
    click.echo("=" * 40)
    click.echo(f"Session ID: {session.get('session_id', 'unknown')}")
    click.echo(f"Project: {session.get('project', 'unknown')}")
    click.echo(f"Path: {session.get('cwd', 'unknown')}")
    click.echo(f"Captured: {session.get('captured_at', 'unknown')}")
    click.echo(f"Processed: {'Yes' if session.get('processed') else 'No'}")
    if session.get("processed_at"):
        click.echo(f"Processed At: {session['processed_at']}")
    if session.get("repo"):
        click.echo(f"Repository: {session['repo']}")
    if session.get("transcript_path"):
        click.echo(f"Transcript: {session['transcript_path']}")


@session.command("stats")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def session_stats(output_format: str) -> None:
    """Show session statistics."""
    from .session import SessionStats

    learnings_dir = Path.home() / ".claude" / "learnings"
    stats_file = learnings_dir / "session_stats.json"

    stats = SessionStats.load(stats_file)

    if output_format == "json":
        click.echo(
            json.dumps(
                {
                    "total": stats.total,
                    "processed": stats.processed,
                    "by_project": stats.by_project,
                    "last_session": stats.last_session,
                },
                indent=2,
            )
        )
    else:
        click.echo("Session Statistics")
        click.echo("=" * 40)
        click.echo(f"Total sessions: {stats.total}")
        click.echo(f"Processed sessions: {stats.processed}")
        click.echo(f"Unprocessed sessions: {stats.total - stats.processed}")
        if stats.last_session:
            click.echo(f"Last session: {stats.last_session}")
        click.echo("")
        click.echo("By Project:")
        for project, count in stats.by_project.items():
            click.echo(f"  {project}: {count}")


@session.command("mark-processed")
@click.argument("session_file")
def session_mark_processed(session_file: str) -> None:
    """Mark a session as processed."""
    from .session import SessionManager

    manager = SessionManager()

    if manager.mark_processed(session_file):
        click.echo(f"Marked session as processed: {session_file}")
    else:
        click.echo(f"Failed to mark session as processed: {session_file}", err=True)
        sys.exit(1)


# === TMUX COMMAND GROUP ===


@main.group("tmux")
def tmux():
    """Manage tmux sessions and navigation."""
    pass


@tmux.command("go")
@click.argument("location")
@click.option("--no-activate", is_flag=True, help="Don't activate iTerm2")
def tmux_go(location: str, no_activate: bool):
    """
    Navigate to tmux session:window.pane and activate iTerm2.

    The location format is 'session:window.pane' where:

      - session: tmux session name

      - window: window index (number)

      - pane: pane index (optional, defaults to 0)

    Examples:

      forge tmux go main:2.1    # Session 'main', window 2, pane 1

      forge tmux go dev:0       # Session 'dev', window 0, pane 0

      forge tmux go work:3      # Session 'work', window 3, pane 0 (implicit)
    """
    from .utils.tmux import TmuxManager

    try:
        manager = TmuxManager()
        session, window, pane = manager.parse_location(location)

        # Validate session exists
        if not manager.session_exists(session):
            click.echo(f"Error: tmux session '{session}' not found", err=True)
            sys.exit(1)

        # Navigate to location
        manager.navigate_to(location)

        # Activate iTerm2 unless disabled
        if not no_activate:
            manager.activate_iterm()

        # Success message
        click.echo(f"Navigated to {location}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nInstall tmux with: brew install tmux", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# === WEBHOOK COMMAND GROUP ===


@main.group("webhook")
def webhook():
    """Manage Claude Code webhook notification system."""
    pass


@webhook.command("init")
@click.option("--skip-deps", is_flag=True, help="Skip dependency installation")
@click.option("--skip-shell", is_flag=True, help="Skip shell configuration")
@click.option("--force", is_flag=True, help="Reinstall even if already installed")
def webhook_init(skip_deps: bool, skip_shell: bool, force: bool):
    """
    Install Claude Code webhook notification system for tmux.

    This sets up native macOS notifications that trigger when Claude Code
    finishes a task or needs your attention. Clicking a notification takes
    you directly to the correct tmux pane.

    Components installed:

      - Python CLI commands (forge notify hook, forge tmux go)

      - Webhook service (LaunchAgent on port 9000)

      - Claude hooks (Stop and Notification)

      - Shell environment (tmux location variables)

      - Configuration files (hooks.json)

    Examples:

      forge webhook init           # Full installation

      forge webhook init --force   # Reinstall everything
    """
    from .utils.webhook import WebhookInstaller

    installer = WebhookInstaller()

    # Check current status
    status = installer.check_status()
    if status["installed"] and not force:
        click.echo("Webhook system already installed. Use --force to reinstall.")
        sys.exit(0)

    try:
        # Install dependencies
        if not skip_deps:
            click.echo("Checking dependencies...")
            deps = installer.check_dependencies()
            missing = [k for k, v in deps.items() if not v]
            if missing:
                click.echo(f"Installing: {', '.join(missing)}")
                installer.install_dependencies()
            else:
                click.echo("All dependencies already installed")

        # Ensure scripts are executable
        click.echo("Checking notification scripts...")
        installer.ensure_scripts_executable()

        # Create hooks.json
        click.echo("Creating webhook configuration...")
        installer.create_hooks_json()

        # Install LaunchAgent
        click.echo("Installing webhook service...")
        installer.install_launchagent()

        # Setup shell
        if not skip_shell:
            click.echo("Configuring shell environment...")
            installer.setup_shell_env()

        # Configure Claude hooks
        click.echo("Configuring Claude Code hooks...")
        installer.configure_claude_hooks()

        click.echo("\n✓ Webhook notification system installed successfully!")
        click.echo("\nNext steps:")
        click.echo("  1. Restart your shell: source ~/.zshrc")
        click.echo("  2. Start Claude Code in a tmux session")
        click.echo("  3. You'll receive notifications when tasks complete")
        click.echo("\nTest with: forge webhook status")

    except Exception as e:
        click.echo(f"Error during installation: {e}", err=True)
        logger.error(f"Webhook installation failed: {e}")
        sys.exit(1)


@webhook.command("status")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def webhook_status(format: str):
    """Check webhook notification system status."""
    from .utils.webhook import WebhookInstaller

    installer = WebhookInstaller()
    status = installer.check_status()

    if format == "json":
        click.echo(json.dumps(status, indent=2))
    else:
        # Pretty text output
        click.echo("Webhook Notification System Status\n")
        click.echo(f"Dependencies:")
        for dep, installed in status.get("dependencies", {}).items():
            icon = "✓" if installed else "✗"
            click.echo(f"  {icon} {dep}")

        click.echo(f"\nCLI Commands:")
        icon = "✓" if status.get("forge_cli_available") else "✗"
        click.echo(f"  {icon} forge notify hook (called by Claude Code hooks)")
        click.echo(f"  {icon} forge tmux go (called by go-tmux webhook)")

        click.echo(f"\nWebhook:")
        icon = "✓" if status.get("hooks_json_configured") else "✗"
        click.echo(f"  {icon} ~/bin/hooks.json (go-tmux only)")
        icon = "✓" if status.get("launchagent_loaded") else "✗"
        click.echo(f"  {icon} LaunchAgent running (port 9000)")

        click.echo(f"\nConfiguration:")
        icon = "✓" if status.get("claude_hooks_configured") else "✗"
        click.echo(f"  {icon} Claude hooks")
        icon = "✓" if status.get("shell_configured") else "✗"
        click.echo(f"  {icon} Shell environment")

        click.echo(f"\nOverall Status: {'✓ Installed' if status.get('installed') else '✗ Not fully installed'}")


# === NOTIFY COMMAND GROUP ===


@main.group("notify")
def notify():
    """Manage macOS notifications for Claude Code."""
    pass


@notify.command("hook")
@click.argument("event", type=click.Choice(["Stop", "Notification"]))
def notify_hook(event: str):
    """
    Wrapper for Claude Code hooks that automatically gathers environment info.

    This command is designed to be called from Claude Code hooks.json.
    It automatically detects tmux environment and sends notifications.

    Usage in hooks.json:

      "hooks": [
        {
          "type": "command",
          "command": "forge notify hook Stop"
        }
      ]

    Environment variables used:
      - WS_TMUX_LOCATION: Tmux location (session:window.pane)
      - WS_TMUX_SESSION_NAME: Tmux session name
      - WS_TMUX_WINDOW_NAME: Tmux window name
      - CLAUDE_SESSION_ID: Claude session ID
      - CLAUDE_TRANSCRIPT_PATH: Path to transcript
      - PWD: Current working directory
      - TMUX: Set when inside tmux (for dynamic detection)
    """
    import os
    import subprocess
    from pathlib import Path
    from .utils.notification import NotificationManager

    # Try to get tmux info dynamically if inside tmux
    if os.environ.get("TMUX"):
        try:
            # Get current tmux location
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#{session_name}:#{window_index}.#{pane_index}"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                tmux_location = result.stdout.strip()
            else:
                tmux_location = os.environ.get("WS_TMUX_LOCATION", "unknown:0")

            # Get session name
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#{session_name}"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            session_name = result.stdout.strip() if result.returncode == 0 else os.environ.get("WS_TMUX_SESSION_NAME", "unknown")

            # Get window name
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#{window_name}"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            window_name = result.stdout.strip() if result.returncode == 0 else os.environ.get("WS_TMUX_WINDOW_NAME", "unknown")

        except Exception:
            # Fallback to env vars
            tmux_location = os.environ.get("WS_TMUX_LOCATION", "unknown:0")
            session_name = os.environ.get("WS_TMUX_SESSION_NAME", "unknown")
            window_name = os.environ.get("WS_TMUX_WINDOW_NAME", "unknown")
    else:
        # Use env vars from tmux-env.sh
        tmux_location = os.environ.get("WS_TMUX_LOCATION")
        session_name = os.environ.get("WS_TMUX_SESSION_NAME")
        window_name = os.environ.get("WS_TMUX_WINDOW_NAME")

        # If no env vars and not in tmux, skip notification
        if not tmux_location:
            sys.exit(0)

    # Get project name from PWD
    cwd = os.environ.get("PWD", os.getcwd())
    project = Path(cwd).name

    # Get other info
    transcript_path = os.environ.get("CLAUDE_TRANSCRIPT_PATH", "")
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")

    try:
        manager = NotificationManager()

        success = manager.send_notification(
            tmux_location=tmux_location,
            session_name=session_name,
            window_name=window_name,
            project=project,
            cwd=cwd,
            transcript_path=transcript_path,
            hook_event=event,
            session_id=session_id,
            skip_focus_check=False,
        )

        sys.exit(0 if success else 1)

    except FileNotFoundError as e:
        # Silently fail if terminal-notifier not installed
        # (hooks should degrade gracefully)
        sys.exit(0)
    except Exception as e:
        # Log error but don't fail the hook
        click.echo(f"Warning: {e}", err=True)
        sys.exit(0)


@notify.command("send")
@click.option("--location", required=True, help="Tmux location (session:window.pane)")
@click.option("--session-name", required=True, help="Tmux session name")
@click.option("--window-name", required=True, help="Tmux window name")
@click.option("--project", required=True, help="Project name")
@click.option("--cwd", required=True, help="Current working directory")
@click.option("--transcript-path", default="", help="Path to transcript file")
@click.option(
    "--event",
    default="Notification",
    help="Hook event name (Stop or Notification)",
)
@click.option("--session-id", default="", help="Claude session ID for grouping")
@click.option(
    "--skip-focus-check",
    is_flag=True,
    help="Skip iTerm2 focus detection",
)
def notify_send(
    location: str,
    session_name: str,
    window_name: str,
    project: str,
    cwd: str,
    transcript_path: str,
    event: str,
    session_id: str,
    skip_focus_check: bool,
):
    """
    Send macOS notification for Claude Code task completion.

    This command is typically called by the webhook service when Claude
    triggers Stop or Notification hooks. It can also be used for testing.

    Examples:

      forge notify send \\
        --location "main:2.1" \\
        --session-name "main" \\
        --window-name "editor" \\
        --project "my-project" \\
        --cwd "/path/to/project" \\
        --event "Stop"

      forge notify send \\
        --location "dev:0" \\
        --session-name "dev" \\
        --window-name "code" \\
        --project "test" \\
        --cwd "/tmp" \\
        --skip-focus-check
    """
    from .utils.notification import NotificationManager

    try:
        manager = NotificationManager()

        success = manager.send_notification(
            tmux_location=location,
            session_name=session_name,
            window_name=window_name,
            project=project,
            cwd=cwd,
            transcript_path=transcript_path,
            hook_event=event,
            session_id=session_id,
            skip_focus_check=skip_focus_check,
        )

        if success:
            click.echo("Notification sent successfully")
            sys.exit(0)
        else:
            click.echo("Failed to send notification (see logs)", err=True)
            sys.exit(1)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo(
            "\nInstall terminal-notifier with: brew install terminal-notifier",
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
