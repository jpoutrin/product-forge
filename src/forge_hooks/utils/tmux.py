"""Manage tmux session navigation and information."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ..common.logging_config import setup_logging

logger = setup_logging()


class TmuxManager:
    """Manage tmux session navigation and information."""

    def __init__(self):
        """Initialize TmuxManager and find tmux binary."""
        self.tmux_bin = self._find_tmux()

    def _find_tmux(self) -> str:
        """
        Find tmux binary using shutil.which() with homebrew fallback.

        Returns:
            Path to tmux binary

        Raises:
            FileNotFoundError: If tmux is not found
        """
        # Try to find tmux in PATH
        tmux_path = shutil.which("tmux")
        if tmux_path:
            logger.debug(f"Found tmux in PATH: {tmux_path}")
            return tmux_path

        # Fallback: Check common Homebrew location on macOS
        homebrew_tmux = "/opt/homebrew/bin/tmux"
        if Path(homebrew_tmux).is_file():
            logger.debug(f"Found tmux at Homebrew location: {homebrew_tmux}")
            return homebrew_tmux

        # Not found
        logger.error("tmux binary not found")
        raise FileNotFoundError("tmux not found. Install with: brew install tmux")

    def parse_location(self, location: str) -> tuple[str, str, Optional[str]]:
        """
        Parse 'session:window.pane' format into components.

        Args:
            location: Location string in format "session:window.pane"
                     Examples: "main:2.1", "dev:0", "work:3"

        Returns:
            Tuple of (session, window, pane)
            - session: tmux session name
            - window: window index
            - pane: pane index or None if not specified

        Raises:
            ValueError: If location format is invalid
        """
        if ":" not in location:
            raise ValueError(
                f"Invalid location format: {location}\n"
                "Expected format: session:window.pane (e.g., 'main:2.1')"
            )

        # Split on ':' to get session and window_pane
        session, window_pane = location.split(":", 1)

        if not session:
            raise ValueError("Session name cannot be empty")

        # Split window_pane on '.' to get window and pane
        if "." in window_pane:
            window, pane = window_pane.split(".", 1)
        else:
            window = window_pane
            pane = None

        if not window:
            raise ValueError("Window index cannot be empty")

        logger.debug(f"Parsed location: session={session}, window={window}, pane={pane}")
        return session, window, pane

    def session_exists(self, session: str) -> bool:
        """
        Check if tmux session exists using 'tmux has-session -t'.

        Args:
            session: Session name to check

        Returns:
            True if session exists, False otherwise
        """
        try:
            result = subprocess.run(
                [self.tmux_bin, "has-session", "-t", session],
                capture_output=True,
                text=True,
                timeout=5,
            )
            exists = result.returncode == 0
            logger.debug(f"Session '{session}' exists: {exists}")
            return exists
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout checking if session '{session}' exists")
            return False
        except Exception as e:
            logger.error(f"Error checking session existence: {e}")
            return False

    def navigate_to(self, location: str) -> None:
        """
        Navigate to session:window.pane.

        Args:
            location: Location string in format "session:window.pane"

        Raises:
            ValueError: If location format is invalid
            RuntimeError: If tmux commands fail
        """
        # Parse location
        session, window, pane = self.parse_location(location)

        logger.info(f"Navigating to tmux location: {location}")

        try:
            # Switch to the session
            result = subprocess.run(
                [self.tmux_bin, "switch-client", "-t", session],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                # switch-client may fail if not inside tmux, that's ok
                logger.debug(f"switch-client returned {result.returncode}: {result.stderr}")

            # Select window
            result = subprocess.run(
                [self.tmux_bin, "select-window", "-t", f"{session}:{window}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.warning(f"Failed to select window: {result.stderr}")
                raise RuntimeError(f"Failed to select window {session}:{window}")

            # Select pane if specified
            if pane is not None:
                result = subprocess.run(
                    [self.tmux_bin, "select-pane", "-t", f"{session}:{window}.{pane}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    logger.warning(f"Failed to select pane: {result.stderr}")
                    raise RuntimeError(f"Failed to select pane {session}:{window}.{pane}")

            logger.info(f"Successfully navigated to {location}")

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout navigating to {location}")
            raise RuntimeError(f"Timeout navigating to {location}")
        except Exception as e:
            logger.error(f"Error navigating to {location}: {e}")
            raise

    def activate_iterm(self) -> None:
        """
        Bring iTerm2 to front (macOS only).

        This method degrades gracefully if not on macOS or iTerm2 is not available.
        """
        try:
            result = subprocess.run(
                ["osascript", "-e", 'tell application "iTerm2" to activate'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                logger.debug("Successfully activated iTerm2")
            else:
                logger.debug(f"Could not activate iTerm2: {result.stderr}")
        except FileNotFoundError:
            logger.debug("osascript not found (not on macOS?)")
        except subprocess.TimeoutExpired:
            logger.warning("Timeout activating iTerm2")
        except Exception as e:
            logger.debug(f"Could not activate iTerm2: {e}")
