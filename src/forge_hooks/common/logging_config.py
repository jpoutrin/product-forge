"""Logging configuration for forge-cli with file-based audit trail."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def get_log_directory() -> Path:
    """
    Get the log directory for forge-cli.

    Can be customized with FORGE_LOG_DIR environment variable.
    Default: ~/.claude/forge/logs/
    """
    log_dir_str = os.environ.get("FORGE_LOG_DIR")
    if log_dir_str:
        log_dir = Path(log_dir_str).expanduser()
    else:
        log_dir = Path.home() / ".claude" / "forge" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
) -> logging.Logger:
    """
    Configure logging with file rotation and console output.

    Environment variables for customization:
        FORGE_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR)
        FORGE_LOG_DIR: Custom log directory path
        FORGE_LOG_FILE: Custom log file name
        FORGE_LOG_CONSOLE: Enable/disable console logging (1/0, true/false)
        FORGE_LOG_MAX_BYTES: Max log file size in bytes (default: 10485760 = 10MB)
        FORGE_LOG_BACKUP_COUNT: Number of backup files to keep (default: 5)

    Args:
        log_level: Logging level (can be overridden by FORGE_LOG_LEVEL env var)
        log_file: Optional log file name (can be overridden by FORGE_LOG_FILE env var)
        enable_console: Whether to also log to console (can be overridden by FORGE_LOG_CONSOLE env var)

    Returns:
        Configured logger instance
    """
    # Read environment variables for customization
    log_level = os.environ.get("FORGE_LOG_LEVEL", log_level)
    log_file = os.environ.get("FORGE_LOG_FILE", log_file or "forge-cli.log")

    console_env = os.environ.get("FORGE_LOG_CONSOLE", "").lower()
    if console_env in ("0", "false", "no"):
        enable_console = False
    elif console_env in ("1", "true", "yes"):
        enable_console = True

    max_bytes = int(os.environ.get("FORGE_LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB default
    backup_count = int(os.environ.get("FORGE_LOG_BACKUP_COUNT", 5))

    # Get root logger
    logger = logging.getLogger("forge_hooks")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    log_path = get_log_directory() / log_file
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (only if enabled)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Log startup
    logger.debug(f"Logging initialized: {log_path}")
    logger.debug(f"Log level: {log_level}, Console: {enable_console}")
    logger.debug(f"Max bytes: {max_bytes}, Backup count: {backup_count}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (use __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_hook_execution(
    hook_type: str,
    operation: str,
    success: bool,
    details: Optional[dict] = None,
) -> None:
    """
    Log hook execution for audit trail.

    Args:
        hook_type: Type of hook (e.g., 'validator', 'feedback')
        operation: Operation performed (e.g., 'new-file', 'save-feedback')
        success: Whether the operation succeeded
        details: Additional details to log
    """
    logger = get_logger("forge_hooks.audit")

    status = "SUCCESS" if success else "FAILURE"
    message = f"Hook execution: {hook_type}.{operation} - {status}"

    if details:
        message += f" | Details: {details}"

    if success:
        logger.info(message)
    else:
        logger.error(message)


def log_validation(
    validator: str,
    passed: bool,
    reason: Optional[str] = None,
    files: Optional[list[str]] = None,
) -> None:
    """
    Log validation results for audit trail.

    Args:
        validator: Name of the validator
        passed: Whether validation passed
        reason: Reason for failure (if applicable)
        files: Files involved in validation
    """
    logger = get_logger("forge_hooks.audit")

    status = "PASSED" if passed else "FAILED"
    message = f"Validation: {validator} - {status}"

    if files:
        message += f" | Files: {', '.join(files)}"

    if reason:
        message += f" | Reason: {reason}"

    if passed:
        logger.info(message)
    else:
        logger.warning(message)
