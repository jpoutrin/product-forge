"""Git operations for file discovery."""

import logging
import subprocess

logger = logging.getLogger(__name__)


def get_git_untracked_files(directory: str, extension: str) -> list[str]:
    """
    Get list of untracked/new files in directory from git status.

    Args:
        directory: Directory to check for files.
        extension: File extension to filter (e.g., '.md', '.py').

    Returns:
        List of file paths matching the extension.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", f"{directory}/"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            logger.info(f"git status returned non-zero: {result.returncode}")
            return []

        untracked = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            # Git status format: XY filename
            # ?? = untracked, A = added, M = modified
            status = line[:2]
            filepath = line[3:].strip()

            # Check for new/untracked files with matching extension
            if status in ("??", "A ", " A", "AM") and filepath.endswith(extension):
                untracked.append(filepath)

        logger.info(f"Git untracked files: {untracked}")
        return untracked
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.warning(f"Git command failed: {e}")
        return []
