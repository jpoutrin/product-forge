"""File discovery utilities for finding recent and new files."""

import logging
import time
from pathlib import Path
from typing import Optional

from .git_utils import get_git_untracked_files

logger = logging.getLogger(__name__)


def get_recent_files(directory: str, extension: str, max_age_minutes: int) -> list[str]:
    """
    Get list of files in directory modified within the last N minutes.

    Args:
        directory: Directory to check for files.
        extension: File extension to filter (e.g., '.md', '.py').
        max_age_minutes: Maximum age in minutes for "recent" files.

    Returns:
        List of file paths matching criteria.
    """
    target_dir = Path(directory)
    if not target_dir.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []

    recent = []
    now = time.time()
    max_age_seconds = max_age_minutes * 60

    # Handle extension with or without leading dot
    ext = extension if extension.startswith(".") else f".{extension}"
    pattern = f"*{ext}"

    for filepath in target_dir.glob(pattern):
        try:
            mtime = filepath.stat().st_mtime
            age = now - mtime
            if age <= max_age_seconds:
                recent.append(str(filepath))
        except OSError as e:
            logger.warning(f"Failed to stat file {filepath}: {e}")
            continue

    logger.info(f"Recent files in {directory}: {len(recent)} files")
    return recent


def find_newest_file(directory: str, extension: str, max_age_minutes: int) -> Optional[str]:
    """
    Find the most recently created/modified file in directory.

    Combines git untracked files and recently modified files, then returns
    the one with the newest modification time.

    Args:
        directory: Directory to check for files.
        extension: File extension to filter (e.g., '.md', '.py').
        max_age_minutes: Maximum age in minutes for "recent" files.

    Returns:
        Path to the newest file, or None if no recent files found.
    """
    # Check git for untracked/new files
    git_new = get_git_untracked_files(directory, extension)

    # Check for recently modified files
    recent_files = get_recent_files(directory, extension, max_age_minutes)

    # Combine and deduplicate
    all_files = list(set(git_new + recent_files))

    if not all_files:
        logger.info(f"No files found in {directory} with extension {extension}")
        return None

    # Find the newest file by modification time
    newest = None
    newest_mtime = 0

    for filepath in all_files:
        try:
            path = Path(filepath)
            if path.exists():
                mtime = path.stat().st_mtime
                if mtime > newest_mtime:
                    newest_mtime = mtime
                    newest = str(path)
        except OSError as e:
            logger.warning(f"Failed to stat file {filepath}: {e}")
            continue

    logger.info(f"Newest file: {newest}")
    return newest
