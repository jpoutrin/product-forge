"""Tests for InitializerOrchestrator."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from forge_hooks.common.init_result import SubsystemResult
from forge_hooks.utils.initializer import InitializerOrchestrator


class TestInitializerOrchestrator:
    """Tests for InitializerOrchestrator class."""

    def test_initialization_with_defaults(self):
        """Test creating orchestrator with default formatter."""
        orchestrator = InitializerOrchestrator()

        assert orchestrator.formatter is not None

    def test_initialization_with_custom_formatter(self):
        """Test creating orchestrator with custom formatter."""
        custom_formatter = Mock()
        orchestrator = InitializerOrchestrator(formatter=custom_formatter)

        assert orchestrator.formatter is custom_formatter

    @patch("forge_hooks.utils.initializer.subprocess.run")
    def test_init_feedback_success(self, mock_run):
        """Test successful feedback initialization."""
        mock_run.return_value = Mock(returncode=0, stderr="")
        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_feedback(force=False)

        assert result.is_success()
        assert result.name == "Feedback/learnings directory"
        mock_run.assert_called_once_with(
            ["forge", "feedback", "init"],
            capture_output=True,
            text=True,
            timeout=10,
        )

    @patch("forge_hooks.utils.initializer.subprocess.run")
    def test_init_feedback_failure(self, mock_run):
        """Test failed feedback initialization."""
        mock_run.return_value = Mock(returncode=1, stderr="Permission denied")
        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_feedback(force=False)

        assert result.is_failed()
        assert result.reason == "Permission denied"

    @patch("forge_hooks.utils.initializer.subprocess.run")
    def test_init_feedback_timeout(self, mock_run):
        """Test feedback initialization timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("forge", 10)
        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_feedback(force=False)

        assert result.is_failed()
        assert "timed out" in result.reason

    @patch("forge_hooks.utils.initializer.subprocess.run")
    def test_init_feedback_exception(self, mock_run):
        """Test feedback initialization with unexpected exception."""
        mock_run.side_effect = Exception("Unexpected error")
        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_feedback(force=False)

        assert result.is_failed()
        assert "Unexpected error" in result.reason

    @patch("forge_hooks.utils.browser_capture.BrowserLogCapture")
    @patch("forge_hooks.utils.browser_capture.get_config_dir")
    def test_init_browser_capture_success_new_install(
        self, mock_get_config_dir, mock_capture_class
    ):
        """Test browser capture initialization with new files."""
        # Setup mocks
        mock_config_dir = Mock()
        mock_config_file = Mock()
        mock_config_file.exists.return_value = False  # Config doesn't exist
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_get_config_dir.return_value = mock_config_dir

        mock_capture = Mock()
        mock_capture.output_dir = Mock()
        mock_capture.output_dir.__truediv__ = Mock(
            return_value=Mock(exists=Mock(return_value=False))
        )  # README doesn't exist
        mock_capture.start_session.return_value = "/tmp/session"
        mock_capture_class.return_value = mock_capture

        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_browser_capture(force=False)

        assert result.is_success()
        assert "Config created" in result.details
        assert "README created" in result.details

    @patch("forge_hooks.utils.browser_capture.BrowserLogCapture")
    @patch("forge_hooks.utils.browser_capture.get_config_dir")
    def test_init_browser_capture_success_existing_install(
        self, mock_get_config_dir, mock_capture_class
    ):
        """Test browser capture initialization with existing files."""
        # Setup mocks
        mock_config_dir = Mock()
        mock_config_file = Mock()
        mock_config_file.exists.return_value = True  # Config exists
        mock_config_dir.__truediv__ = Mock(return_value=mock_config_file)
        mock_get_config_dir.return_value = mock_config_dir

        mock_capture = Mock()
        mock_capture.output_dir = Mock()
        mock_capture.output_dir.__truediv__ = Mock(
            return_value=Mock(exists=Mock(return_value=True))
        )  # README exists
        mock_capture.start_session.return_value = "/tmp/session"
        mock_capture_class.return_value = mock_capture

        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_browser_capture(force=False)

        assert result.is_success()
        assert "Config exists" in result.details
        assert "README exists" in result.details

    @patch("forge_hooks.utils.browser_capture.BrowserLogCapture")
    def test_init_browser_capture_failure(self, mock_capture_class):
        """Test browser capture initialization failure."""
        mock_capture_class.side_effect = Exception("Import error")
        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_browser_capture(force=False)

        assert result.is_failed()
        assert "Import error" in result.reason

    @patch("forge_hooks.utils.initializer.subprocess.run")
    @patch("forge_hooks.utils.webhook.WebhookInstaller")
    def test_init_webhook_success(self, mock_installer_class, mock_run):
        """Test successful webhook initialization."""
        # Setup mocks
        mock_installer = Mock()
        mock_installer.check_status.return_value = {"installed": False}
        mock_installer_class.return_value = mock_installer

        mock_run.return_value = Mock(returncode=0)

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()
        orchestrator.formatter.confirm_webhook_install.return_value = True

        result = orchestrator._init_webhook(force=False)

        assert result.is_success()

    @patch("forge_hooks.utils.webhook.WebhookInstaller")
    def test_init_webhook_already_installed(self, mock_installer_class):
        """Test webhook initialization when already installed."""
        mock_installer = Mock()
        mock_installer.check_status.return_value = {"installed": True}
        mock_installer_class.return_value = mock_installer

        orchestrator = InitializerOrchestrator()

        result = orchestrator._init_webhook(force=False)

        assert result.is_skipped()
        assert "already installed" in result.reason

    @patch("forge_hooks.utils.initializer.subprocess.run")
    @patch("forge_hooks.utils.webhook.WebhookInstaller")
    def test_init_webhook_force_reinstall(self, mock_installer_class, mock_run):
        """Test webhook force reinstall."""
        mock_installer = Mock()
        mock_installer.check_status.return_value = {"installed": True}
        mock_installer_class.return_value = mock_installer

        mock_run.return_value = Mock(returncode=0)

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()

        result = orchestrator._init_webhook(force=True)

        # Should not prompt when force=True
        orchestrator.formatter.confirm_webhook_install.assert_not_called()
        assert result.is_success()
        # Verify --force flag was passed
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "--force" in args

    @patch("forge_hooks.utils.webhook.WebhookInstaller")
    def test_init_webhook_user_declined(self, mock_installer_class):
        """Test webhook initialization when user declines."""
        mock_installer = Mock()
        mock_installer.check_status.return_value = {"installed": False}
        mock_installer_class.return_value = mock_installer

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()
        orchestrator.formatter.confirm_webhook_install.return_value = False

        result = orchestrator._init_webhook(force=False)

        assert result.is_skipped()
        assert "user declined" in result.reason

    def test_init_webhook_import_error(self):
        """Test webhook initialization with missing dependencies."""
        with patch("forge_hooks.utils.webhook.WebhookInstaller") as mock_import:
            mock_import.side_effect = ImportError("Module not found")

            orchestrator = InitializerOrchestrator()

            result = orchestrator._init_webhook(force=False)

            assert result.is_skipped()
            assert "not available" in result.reason

    @patch("forge_hooks.utils.initializer.subprocess.run")
    @patch("forge_hooks.utils.webhook.WebhookInstaller")
    def test_init_webhook_installation_failed(self, mock_installer_class, mock_run):
        """Test webhook installation failure."""
        mock_installer = Mock()
        mock_installer.check_status.return_value = {"installed": False}
        mock_installer_class.return_value = mock_installer

        mock_run.return_value = Mock(returncode=1)

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()
        orchestrator.formatter.confirm_webhook_install.return_value = True

        result = orchestrator._init_webhook(force=False)

        assert result.is_failed()
        assert "installation failed" in result.reason

    @patch.object(InitializerOrchestrator, "_init_feedback")
    @patch.object(InitializerOrchestrator, "_init_browser_capture")
    @patch.object(InitializerOrchestrator, "_init_webhook")
    def test_initialize_all_success(
        self, mock_webhook, mock_browser, mock_feedback
    ):
        """Test initializing all subsystems successfully."""
        mock_feedback.return_value = SubsystemResult(
            name="Feedback", status="success"
        )
        mock_browser.return_value = SubsystemResult(
            name="Browser", status="success"
        )
        mock_webhook.return_value = SubsystemResult(
            name="Webhook", status="success"
        )

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()

        results = orchestrator.initialize_all()

        assert len(results) == 3
        assert results.has_successes()
        assert not results.has_failures()

    @patch.object(InitializerOrchestrator, "_init_feedback")
    @patch.object(InitializerOrchestrator, "_init_browser_capture")
    @patch.object(InitializerOrchestrator, "_init_webhook")
    def test_initialize_all_skip_webhook(
        self, mock_webhook, mock_browser, mock_feedback
    ):
        """Test initializing with webhook skipped."""
        mock_feedback.return_value = SubsystemResult(
            name="Feedback", status="success"
        )
        mock_browser.return_value = SubsystemResult(
            name="Browser", status="success"
        )

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()

        results = orchestrator.initialize_all(skip_webhook=True)

        # Webhook should not be called
        mock_webhook.assert_not_called()

        # Should have 3 results (2 success, 1 skipped)
        assert len(results) == 3
        skipped = results.get_skipped()
        assert any("Webhook" in s for s in skipped)

    @patch.object(InitializerOrchestrator, "_init_feedback")
    @patch.object(InitializerOrchestrator, "_init_browser_capture")
    @patch.object(InitializerOrchestrator, "_init_webhook")
    def test_initialize_all_mixed_results(
        self, mock_webhook, mock_browser, mock_feedback
    ):
        """Test initialization with mixed success/skip/failure."""
        mock_feedback.return_value = SubsystemResult(
            name="Feedback", status="success"
        )
        mock_browser.return_value = SubsystemResult(
            name="Browser", status="skipped", reason="already exists"
        )
        mock_webhook.return_value = SubsystemResult(
            name="Webhook", status="failed", reason="permission denied"
        )

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()

        results = orchestrator.initialize_all()

        assert len(results) == 3
        assert results.has_successes()
        assert results.has_failures()
        assert len(results.get_successful()) == 1
        assert len(results.get_skipped()) == 1
        assert len(results.get_failed()) == 1

    @patch.object(InitializerOrchestrator, "_init_feedback")
    @patch.object(InitializerOrchestrator, "_init_browser_capture")
    @patch.object(InitializerOrchestrator, "_init_webhook")
    def test_initialize_all_skip_all(
        self, mock_webhook, mock_browser, mock_feedback
    ):
        """Test initialization with all subsystems skipped."""
        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()

        results = orchestrator.initialize_all(
            skip_feedback=True,
            skip_browser=True,
            skip_webhook=True,
        )

        # No init methods should be called
        mock_feedback.assert_not_called()
        mock_browser.assert_not_called()
        mock_webhook.assert_not_called()

        # All should be marked as skipped
        assert len(results) == 3
        assert len(results.get_skipped()) == 3
        assert not results.has_successes()

    @patch.object(InitializerOrchestrator, "_init_feedback")
    @patch.object(InitializerOrchestrator, "_init_browser_capture")
    @patch.object(InitializerOrchestrator, "_init_webhook")
    def test_initialize_all_force_flag_propagated(
        self, mock_webhook, mock_browser, mock_feedback
    ):
        """Test that force flag is propagated to all init methods."""
        mock_feedback.return_value = SubsystemResult(
            name="Feedback", status="success"
        )
        mock_browser.return_value = SubsystemResult(
            name="Browser", status="success"
        )
        mock_webhook.return_value = SubsystemResult(
            name="Webhook", status="success"
        )

        orchestrator = InitializerOrchestrator()
        orchestrator.formatter = Mock()

        results = orchestrator.initialize_all(force=True)

        # Verify force=True was passed to all methods
        mock_feedback.assert_called_once_with(force=True)
        mock_browser.assert_called_once_with(force=True)
        mock_webhook.assert_called_once_with(force=True)
