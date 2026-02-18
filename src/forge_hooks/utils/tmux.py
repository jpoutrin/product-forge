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

    def _run_applescript(self, script: str) -> Optional[str]:
        """
        Execute AppleScript and return output.

        Args:
            script: AppleScript code to execute

        Returns:
            Script output (stdout.strip()) on success, None on error
        """
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.debug(f"AppleScript output: {output}")
                return output
            else:
                logger.debug(f"AppleScript failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.warning("Timeout executing AppleScript")
            return None
        except FileNotFoundError:
            logger.debug("osascript not found (not on macOS?)")
            return None
        except Exception as e:
            logger.debug(f"Error executing AppleScript: {e}")
            return None

    def _get_iterm_tabs(self) -> list[dict]:
        """
        Get list of all iTerm2 tabs with their metadata.

        Returns:
            List of dicts with keys: window_id, tab_id, session_id, tab_name,
            window_index, tab_index
        """
        # AppleScript to iterate all windows and tabs
        script = '''
        tell application "iTerm2"
            set output to ""
            repeat with w in windows
                set window_id to id of w
                set window_index to index of w
                repeat with t in tabs of w
                    set tab_id to id of t
                    set tab_index to index of t
                    set session_id to id of current session of t
                    set tab_name to name of current session of t
                    set output to output & window_id & "|" & tab_id & "|" & session_id & "|" & tab_name & "|" & window_index & "|" & tab_index & "\\n"
                end repeat
            end repeat
            return output
        end tell
        '''

        output = self._run_applescript(script)
        if not output:
            logger.debug("No iTerm2 tabs found or AppleScript failed")
            return []

        tabs = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 6:
                logger.debug(f"Skipping malformed tab line: {line}")
                continue

            tabs.append({
                "window_id": parts[0],
                "tab_id": parts[1],
                "session_id": parts[2],
                "tab_name": parts[3],
                "window_index": parts[4],
                "tab_index": parts[5],
            })

        logger.debug(f"Found {len(tabs)} iTerm2 tabs")
        return tabs

    def _find_matching_tab(
        self, session_name: str, tabs: list[dict]
    ) -> Optional[dict]:
        """
        Find iTerm2 tab matching the session name.

        Args:
            session_name: Tmux session name to match
            tabs: List of tab dicts from _get_iterm_tabs()

        Returns:
            First matching tab dict or None
        """
        matches = [tab for tab in tabs if tab["tab_name"] == session_name]

        if not matches:
            logger.debug(f"No tab found matching session name: {session_name}")
            return None

        if len(matches) > 1:
            logger.warning(
                f"Multiple tabs match session name '{session_name}', using first"
            )

        match = matches[0]
        logger.debug(
            f"Found matching tab: {match['tab_name']} "
            f"(window {match['window_index']}, tab {match['tab_index']})"
        )
        return match

    def _is_tmux_running_in_tab(self, session_id: str) -> bool:
        """
        Check if tmux is running in the specified iTerm2 session.

        Args:
            session_id: iTerm2 session ID

        Returns:
            True if tmux is running, False otherwise
        """
        script = f'''
        tell application "iTerm2"
            repeat with w in windows
                repeat with t in tabs of w
                    if id of current session of t is "{session_id}" then
                        return name of current session of t
                    end if
                end repeat
            end repeat
        end tell
        '''

        output = self._run_applescript(script)
        if not output:
            logger.debug(f"Could not get process name for session {session_id}")
            return False

        is_running = "tmux" in output.lower()
        logger.debug(f"Session process: '{output}' - tmux running: {is_running}")
        return is_running

    def _focus_iterm_tab(self, window_id: str, tab_id: str) -> bool:
        """
        Focus a specific iTerm2 tab.

        Args:
            window_id: iTerm2 window ID
            tab_id: iTerm2 tab ID

        Returns:
            True on success, False on failure
        """
        script = f'''
        tell application "iTerm2"
            repeat with w in windows
                if id of w is "{window_id}" then
                    repeat with t in tabs of w
                        if id of t is "{tab_id}" then
                            select t
                            activate
                            return "success"
                        end if
                    end repeat
                end if
            end repeat
            return "not found"
        end tell
        '''

        output = self._run_applescript(script)
        success = output == "success"

        if success:
            logger.info(f"Focused iTerm2 tab: window={window_id}, tab={tab_id}")
        else:
            logger.warning(f"Failed to focus iTerm2 tab: window={window_id}, tab={tab_id}")

        return success

    def activate_iterm_intelligent(self, session_name: str) -> None:
        """
        Intelligently activate iTerm2 and focus the appropriate tab.

        Strategy:
        1. If tab name matches session_name and tmux is running → focus that tab
        2. Else if "tmux" tab exists → focus that tab
        3. Else → fall back to basic iTerm2 activation

        Args:
            session_name: Tmux session name to match against tab names

        This method degrades gracefully to activate_iterm() on any error.
        """
        try:
            # Get all iTerm2 tabs
            tabs = self._get_iterm_tabs()
            if not tabs:
                logger.info("No iTerm2 tabs found, using basic activation")
                self.activate_iterm()
                return

            # Try to find matching tab
            matching_tab = self._find_matching_tab(session_name, tabs)
            if matching_tab:
                # Check if tmux is actually running in this tab
                if self._is_tmux_running_in_tab(matching_tab["session_id"]):
                    logger.info(
                        f"Focusing tab '{matching_tab['tab_name']}' "
                        f"(matches session '{session_name}' and tmux is running)"
                    )
                    self._focus_iterm_tab(
                        matching_tab["window_id"], matching_tab["tab_id"]
                    )
                    return
                else:
                    logger.info(
                        f"Tab '{matching_tab['tab_name']}' matches session name "
                        "but tmux not running, falling back to 'tmux' tab"
                    )

            # Try to find "tmux" tab as fallback
            tmux_tab = self._find_matching_tab("tmux", tabs)
            if tmux_tab:
                logger.info("Focusing default 'tmux' tab")
                self._focus_iterm_tab(tmux_tab["window_id"], tmux_tab["tab_id"])
                return

            # Final fallback: basic activation
            logger.info("No special tabs found, using basic iTerm2 activation")
            self.activate_iterm()

        except Exception as e:
            logger.error(f"Error in intelligent iTerm2 focusing: {e}")
            logger.info("Falling back to basic iTerm2 activation")
            self.activate_iterm()
