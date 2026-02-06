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


if __name__ == "__main__":
    main()
