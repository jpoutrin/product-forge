"""Tests for macOS notification manager."""

from unittest.mock import Mock, patch

import pytest

from forge_hooks.utils.notification import NotificationManager


class TestNotificationManager:
    """Test cases for NotificationManager."""

    # Binary detection tests
    @patch("shutil.which")
    def test_find_terminal_notifier_in_path(self, mock_which):
        """Test finding terminal-notifier in PATH."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        assert manager.terminal_notifier == "/usr/local/bin/terminal-notifier"

    @patch("shutil.which")
    @patch("pathlib.Path.is_file")
    def test_find_terminal_notifier_homebrew(self, mock_is_file, mock_which):
        """Test finding terminal-notifier in Homebrew location."""
        mock_which.return_value = None
        mock_is_file.return_value = True

        manager = NotificationManager()

        assert manager.terminal_notifier == "/opt/homebrew/bin/terminal-notifier"

    @patch("shutil.which")
    @patch("pathlib.Path.is_file")
    def test_find_terminal_notifier_not_found(self, mock_is_file, mock_which):
        """Test error when terminal-notifier not found."""
        mock_which.return_value = None
        mock_is_file.return_value = False

        with pytest.raises(FileNotFoundError, match="terminal-notifier not found"):
            NotificationManager()

    # Focus detection tests
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_frontmost_app_iterm2(self, mock_run, mock_which):
        """Test detecting iTerm2 as frontmost app."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"
        mock_run.return_value = Mock(returncode=0, stdout="iTerm2\n")

        manager = NotificationManager()
        app = manager._get_frontmost_app()

        assert app == "iTerm2"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_frontmost_app_other(self, mock_run, mock_which):
        """Test detecting non-iTerm2 frontmost app."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"
        mock_run.return_value = Mock(returncode=0, stdout="Chrome\n")

        manager = NotificationManager()
        app = manager._get_frontmost_app()

        assert app == "Chrome"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_frontmost_app_error(self, mock_run, mock_which):
        """Test error handling when getting frontmost app fails."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"
        mock_run.return_value = Mock(returncode=1, stderr="error")

        manager = NotificationManager()
        app = manager._get_frontmost_app()

        assert app is None

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_active_tmux_session_window(self, mock_run, mock_which):
        """Test parsing tmux list-clients output."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"
        mock_run.return_value = Mock(
            returncode=0, stdout="1234567890 main:2\n1234567891 dev:0\n"
        )

        manager = NotificationManager()
        session_window = manager._get_active_tmux_session_window()

        # Should return the most recent (highest timestamp)
        assert session_window == "dev:0"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_get_active_tmux_session_window_error(self, mock_run, mock_which):
        """Test error handling when tmux list-clients fails."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"
        mock_run.return_value = Mock(returncode=1, stderr="error")

        manager = NotificationManager()
        session_window = manager._get_active_tmux_session_window()

        assert session_window is None

    # URL encoding tests
    @patch("shutil.which")
    def test_url_encode_basic(self, mock_which):
        """Test URL encoding basic string."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()
        encoded = manager._url_encode("main:2.1")

        assert encoded == "main%3A2.1"

    @patch("shutil.which")
    def test_url_encode_special_chars(self, mock_which):
        """Test URL encoding with special characters."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()
        encoded = manager._url_encode("test session:0.1")

        assert encoded == "test%20session%3A0.1"

    # Extract session:window tests
    @patch("shutil.which")
    def test_extract_session_window_with_pane(self, mock_which):
        """Test extracting session:window from session:window.pane."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()
        session_window = manager._extract_session_window("main:2.1")

        assert session_window == "main:2"

    @patch("shutil.which")
    def test_extract_session_window_without_pane(self, mock_which):
        """Test extracting session:window when no pane is specified."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()
        session_window = manager._extract_session_window("main:2")

        assert session_window == "main:2"

    # Focus detection logic tests
    @patch("shutil.which")
    def test_should_skip_notification_when_focused(self, mock_which):
        """Test skipping notification when focused on same location."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        with patch.object(manager, "_get_frontmost_app", return_value="iTerm2"), patch.object(
            manager, "_get_active_tmux_session_window", return_value="main:2"
        ):
            should_skip = manager.should_skip_notification("main:2.1")

            assert should_skip is True

    @patch("shutil.which")
    def test_should_not_skip_when_different_location(self, mock_which):
        """Test sending notification for different location."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        with patch.object(manager, "_get_frontmost_app", return_value="iTerm2"), patch.object(
            manager, "_get_active_tmux_session_window", return_value="main:2"
        ):
            should_skip = manager.should_skip_notification("dev:0")

            assert should_skip is False

    @patch("shutil.which")
    def test_should_not_skip_when_not_iterm2(self, mock_which):
        """Test sending notification when iTerm2 is not frontmost."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        with patch.object(manager, "_get_frontmost_app", return_value="Chrome"):
            should_skip = manager.should_skip_notification("main:2.1")

            assert should_skip is False

    # Command building tests
    @patch("shutil.which")
    def test_build_notification_command_stop(self, mock_which):
        """Test building command for Stop event."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()
        cmd = manager._build_notification_command(
            tmux_location="main:2.1",
            session_name="main",
            window_name="editor",
            project="test-project",
            hook_event="Stop",
            session_id="abc123",
        )

        assert cmd[0] == "/usr/local/bin/terminal-notifier"
        assert "-title" in cmd
        assert "Claude Code - main" in cmd
        assert "-subtitle" in cmd
        assert "Claude is done" in cmd
        assert "-sound" in cmd
        assert "Glass" in cmd
        assert "-group" in cmd
        assert "claude-abc123" in cmd

    @patch("shutil.which")
    def test_build_notification_command_notification(self, mock_which):
        """Test building command for Notification event."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()
        cmd = manager._build_notification_command(
            tmux_location="dev:0",
            session_name="dev",
            window_name="code",
            project="my-app",
            hook_event="Notification",
            session_id="xyz789",
        )

        assert "-subtitle" in cmd
        assert "Claude is waiting" in cmd
        assert "-sound" in cmd
        assert "default" in cmd

    @patch("shutil.which")
    def test_build_notification_command_with_sender(self, mock_which, monkeypatch):
        """Test building command with NOTIFICATION_SENDER env var."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"
        monkeypatch.setenv("NOTIFICATION_SENDER", "com.apple.Terminal")

        manager = NotificationManager()
        cmd = manager._build_notification_command(
            tmux_location="main:2.1",
            session_name="main",
            window_name="editor",
            project="test",
            hook_event="Stop",
            session_id="abc",
        )

        assert "-sender" in cmd
        assert "com.apple.Terminal" in cmd

    # Integration tests
    @patch("shutil.which")
    @patch("subprocess.Popen")
    def test_send_notification_success(self, mock_popen, mock_which):
        """Test successful notification send."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        with patch.object(manager, "should_skip_notification", return_value=False):
            success = manager.send_notification(
                tmux_location="main:2.1",
                session_name="main",
                window_name="editor",
                project="test",
                cwd="/tmp",
                transcript_path="",
                hook_event="Stop",
                session_id="abc123",
            )

            assert success is True
            mock_popen.assert_called_once()

    @patch("shutil.which")
    def test_send_notification_skipped_when_focused(self, mock_which):
        """Test notification skipped when already focused."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        with patch.object(manager, "should_skip_notification", return_value=True):
            success = manager.send_notification(
                tmux_location="main:2.1",
                session_name="main",
                window_name="editor",
                project="test",
                cwd="/tmp",
                transcript_path="",
                hook_event="Stop",
                session_id="abc123",
            )

            assert success is True

    @patch("shutil.which")
    @patch("subprocess.Popen")
    def test_send_notification_skip_focus_check(self, mock_popen, mock_which):
        """Test sending notification with skip_focus_check flag."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        success = manager.send_notification(
            tmux_location="main:2.1",
            session_name="main",
            window_name="editor",
            project="test",
            cwd="/tmp",
            transcript_path="",
            hook_event="Stop",
            session_id="abc123",
            skip_focus_check=True,
        )

        assert success is True
        mock_popen.assert_called_once()

    @patch("shutil.which")
    @patch("subprocess.Popen")
    def test_send_notification_extracts_project_from_cwd(self, mock_popen, mock_which):
        """Test extracting project name from cwd when project is unknown."""
        mock_which.return_value = "/usr/local/bin/terminal-notifier"

        manager = NotificationManager()

        with patch.object(manager, "should_skip_notification", return_value=False):
            success = manager.send_notification(
                tmux_location="main:2.1",
                session_name="main",
                window_name="editor",
                project="unknown",
                cwd="/home/user/my-project",
                transcript_path="",
                hook_event="Stop",
                session_id="abc123",
            )

            assert success is True
            # Verify the command includes the extracted project name
            call_args = mock_popen.call_args[0][0]
            assert "my-project" in " ".join(call_args)
