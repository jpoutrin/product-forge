"""Manage macOS notifications for Claude Code sessions."""

import shutil
import subprocess
import urllib.parse
from typing import Optional

from ..common.logging_config import setup_logging

logger = setup_logging()


class NotificationManager:
    """Manage macOS notifications for Claude Code sessions."""

    def __init__(self):
        """Initialize and find terminal-notifier binary."""
        self.terminal_notifier = self._find_terminal_notifier()
        self.webhook_url = "http://localhost:9000/hooks/go-tmux"

    def _find_terminal_notifier(self) -> str:
        """
        Find terminal-notifier binary using shutil.which() with homebrew fallback.

        Returns:
            Path to terminal-notifier binary

        Raises:
            FileNotFoundError: If terminal-notifier is not found
        """
        # Try to find terminal-notifier in PATH
        notifier_path = shutil.which("terminal-notifier")
        if notifier_path:
            logger.debug(f"Found terminal-notifier in PATH: {notifier_path}")
            return notifier_path

        # Fallback: Check common Homebrew location on macOS
        homebrew_notifier = "/opt/homebrew/bin/terminal-notifier"
        from pathlib import Path

        if Path(homebrew_notifier).is_file():
            logger.debug(f"Found terminal-notifier at Homebrew location: {homebrew_notifier}")
            return homebrew_notifier

        # Not found
        logger.error("terminal-notifier binary not found")
        raise FileNotFoundError(
            "terminal-notifier not found. Install with: brew install terminal-notifier"
        )

    def send_notification(
        self,
        tmux_location: str,
        session_name: str,
        window_name: str,
        project: str,
        cwd: str,
        transcript_path: str,
        hook_event: str,
        session_id: str,
        skip_focus_check: bool = False,
    ) -> bool:
        """
        Send macOS notification for Claude Code task completion.

        Args:
            tmux_location: Tmux location (session:window.pane)
            session_name: Tmux session name
            window_name: Tmux window name
            project: Project name
            cwd: Current working directory
            transcript_path: Path to transcript file
            hook_event: Hook event name (Stop or Notification)
            session_id: Claude session ID for grouping
            skip_focus_check: Skip iTerm2 focus detection

        Returns:
            True on success, False on failure
        """
        # Check focus detection (unless skipped)
        if not skip_focus_check:
            if self.should_skip_notification(tmux_location):
                logger.info(
                    f"Skipping notification: Already focused on {tmux_location}"
                )
                return True  # Successfully skipped, not an error

        # Extract project name from CWD if unknown
        if not project or project == "unknown":
            from pathlib import Path

            project = Path(cwd).name if cwd else "unknown"

        # Build and execute terminal-notifier command
        cmd = self._build_notification_command(
            tmux_location=tmux_location,
            session_name=session_name,
            window_name=window_name,
            project=project,
            hook_event=hook_event,
            session_id=session_id,
        )

        try:
            # Run in background (don't wait)
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(
                f"Notification sent: {hook_event} for {project} in {tmux_location}"
            )
            return True

        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
            return False

    def should_skip_notification(self, tmux_location: str) -> bool:
        """
        Check if notification should be skipped due to focus detection.

        Level 1: Check if iTerm2 is frontmost
        Level 2: Get current tmux session:window
        Level 3: Compare with notification location (strip pane)

        Args:
            tmux_location: Notification location (session:window.pane)

        Returns:
            True if should skip (already focused), False otherwise
        """
        # Level 1: Check if iTerm2 is frontmost application
        frontmost_app = self._get_frontmost_app()
        if frontmost_app != "iTerm2":
            logger.debug(f"Frontmost app is {frontmost_app}, not iTerm2 - send notification")
            return False

        # Level 2: Get current active tmux session:window
        current_session_window = self._get_active_tmux_session_window()
        if not current_session_window:
            logger.debug("Cannot detect current tmux session:window - send notification")
            return False

        # Level 3: Compare session:window (ignore pane)
        notification_session_window = self._extract_session_window(tmux_location)
        if current_session_window == notification_session_window:
            logger.debug(
                f"Already focused on {current_session_window} - skip notification"
            )
            return True
        else:
            logger.debug(
                f"Different location: current={current_session_window}, "
                f"notification={notification_session_window} - send notification"
            )
            return False

    def _get_frontmost_app(self) -> Optional[str]:
        """
        Get the frontmost application name using AppleScript.

        Returns:
            Application name or None on error
        """
        try:
            result = subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to get name of first application process whose frontmost is true',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                app_name = result.stdout.strip()
                logger.debug(f"Frontmost app: {app_name}")
                return app_name
            else:
                logger.debug(f"Could not get frontmost app: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting frontmost app")
            return None
        except Exception as e:
            logger.debug(f"Error getting frontmost app: {e}")
            return None

    def _get_active_tmux_session_window(self) -> Optional[str]:
        """
        Get the most recently active tmux session:window.

        Parses output of 'tmux list-clients' to find most recent client's location.

        Returns:
            session:window or None on error
        """
        try:
            result = subprocess.run(
                ["tmux", "list-clients", "-F", "#{client_activity} #{session_name}:#{window_index}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.debug(f"tmux list-clients failed: {result.stderr}")
                return None

            # Parse output: "timestamp session:window"
            # Sort by timestamp descending and take the first (most recent)
            lines = result.stdout.strip().split("\n")
            if not lines or not lines[0]:
                logger.debug("No tmux clients found")
                return None

            # Sort by timestamp (first field) in reverse numerical order
            sorted_lines = sorted(lines, key=lambda x: int(x.split()[0]) if x.split() else 0, reverse=True)
            if sorted_lines and sorted_lines[0]:
                # Extract session:window from "timestamp session:window"
                parts = sorted_lines[0].split(maxsplit=1)
                if len(parts) == 2:
                    session_window = parts[1]
                    logger.debug(f"Active tmux session:window: {session_window}")
                    return session_window

            logger.debug("Could not parse tmux client info")
            return None

        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting active tmux session")
            return None
        except Exception as e:
            logger.debug(f"Error getting active tmux session: {e}")
            return None

    def _extract_session_window(self, location: str) -> str:
        """
        Extract session:window from full location (strip pane).

        Args:
            location: Full location (e.g., "main:2.1" or "main:2")

        Returns:
            session:window (e.g., "main:2")
        """
        # Remove .pane suffix if present: "main:2.1" -> "main:2"
        return location.split(".")[0]

    def _url_encode(self, text: str) -> str:
        """
        URL-encode text for use in webhook POST.

        Args:
            text: Text to encode

        Returns:
            URL-encoded string
        """
        return urllib.parse.quote(text, safe="")

    def _build_notification_command(
        self,
        tmux_location: str,
        session_name: str,
        window_name: str,
        project: str,
        hook_event: str,
        session_id: str,
    ) -> list[str]:
        """
        Build terminal-notifier command list.

        Args:
            tmux_location: Tmux location (session:window.pane)
            session_name: Tmux session name
            window_name: Tmux window name
            project: Project name
            hook_event: Hook event name (Stop or Notification)
            session_id: Claude session ID for grouping

        Returns:
            Command list for subprocess
        """
        # Determine status and sound based on event
        if hook_event == "Stop":
            subtitle = "Claude is done"
            sound = "Glass"
        else:
            subtitle = "Claude is waiting"
            sound = "default"

        # URL-encode the tmux location for click action
        encoded_location = self._url_encode(tmux_location)

        # Build command
        cmd = [
            self.terminal_notifier,
            "-title",
            f"Claude Code - {session_name}",
            "-subtitle",
            subtitle,
            "-message",
            f"Project: {project} (window: {window_name})",
            "-execute",
            f"/usr/bin/curl -s -X POST '{self.webhook_url}?tmux_location={encoded_location}'",
            "-sound",
            sound,
            "-group",
            f"claude-{session_id}",
        ]

        # Add sender argument if NOTIFICATION_SENDER env var is set
        import os

        sender = os.environ.get("NOTIFICATION_SENDER")
        if sender:
            cmd.extend(["-sender", sender])

        logger.debug(f"Built notification command: {' '.join(cmd[:6])}...")
        return cmd
