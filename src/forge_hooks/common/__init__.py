"""Common utilities for forge-hooks."""

from .file_discovery import find_newest_file, get_recent_files
from .git_utils import get_git_untracked_files
from .hook_io import HookResult, output_result, read_hook_input
from .logging_config import (
    get_log_directory,
    get_logger,
    log_hook_execution,
    log_validation,
    setup_logging,
)

__all__ = [
    "HookResult",
    "read_hook_input",
    "output_result",
    "find_newest_file",
    "get_recent_files",
    "get_git_untracked_files",
    "setup_logging",
    "get_logger",
    "get_log_directory",
    "log_hook_execution",
    "log_validation",
]
