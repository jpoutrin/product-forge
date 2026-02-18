"""Tests for initialization output formatting."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from forge_hooks.common.init_output import InitOutputFormatter
from forge_hooks.common.init_result import InitializationResult, SubsystemResult


class TestInitOutputFormatter:
    """Tests for InitOutputFormatter class."""

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_header(self, mock_echo):
        """Test printing initialization header."""
        InitOutputFormatter.print_header()

        mock_echo.assert_called_once_with("🚀 Initializing Product Forge subsystems...\n")

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_subsystem_start_default_emoji(self, mock_echo):
        """Test printing subsystem start with default emoji."""
        InitOutputFormatter.print_subsystem_start("browser capture system")

        mock_echo.assert_called_once_with("📦 Setting up browser capture system...")

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_subsystem_start_custom_emoji(self, mock_echo):
        """Test printing subsystem start with custom emoji."""
        InitOutputFormatter.print_subsystem_start("feedback directory", emoji="📚")

        mock_echo.assert_called_once_with("📚 Setting up feedback directory...")

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_subsystem_result_success_with_details(self, mock_echo):
        """Test printing successful result with details."""
        result = SubsystemResult(
            name="Browser capture",
            status="success",
            details={"Config created": "~/.claude/forge/config/browser-capture.yaml"},
        )

        InitOutputFormatter.print_subsystem_result(result)

        # Should print detail and blank line
        assert mock_echo.call_count == 2
        first_call = mock_echo.call_args_list[0][0][0]
        assert "✅" in first_call
        assert "Config created" in first_call

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_subsystem_result_success_without_details(self, mock_echo):
        """Test printing successful result without details."""
        result = SubsystemResult(name="Browser capture", status="success")

        InitOutputFormatter.print_subsystem_result(result)

        # Should print generic success and blank line
        assert mock_echo.call_count == 2
        first_call = mock_echo.call_args_list[0][0][0]
        assert "✅" in first_call
        assert "Browser capture initialized" in first_call

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_subsystem_result_skipped_with_reason(self, mock_echo):
        """Test printing skipped result with reason."""
        result = SubsystemResult(
            name="Webhook system", status="skipped", reason="already installed"
        )

        InitOutputFormatter.print_subsystem_result(result)

        # Should print skip reason and blank line
        assert mock_echo.call_count == 2
        first_call = mock_echo.call_args_list[0][0][0]
        assert "⏭️" in first_call
        assert "already installed" in first_call

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_subsystem_result_failed(self, mock_echo):
        """Test printing failed result."""
        result = SubsystemResult(
            name="Feedback directory", status="failed", reason="Permission denied"
        )

        InitOutputFormatter.print_subsystem_result(result)

        # Should print error to stderr and blank line
        assert mock_echo.call_count == 2
        first_call_args = mock_echo.call_args_list[0]
        assert "❌" in first_call_args[0][0]
        assert "Permission denied" in first_call_args[0][0]
        assert first_call_args[1]["err"] is True  # Check stderr flag

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_config_status_created(self, mock_echo):
        """Test printing config status when created."""
        InitOutputFormatter.print_config_status(
            "~/.claude/forge/config/test.yaml", existed=False, created=True
        )

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "✅" in call_text
        assert "Config created" in call_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_config_status_existed(self, mock_echo):
        """Test printing config status when already existed."""
        InitOutputFormatter.print_config_status(
            "~/.claude/forge/config/test.yaml", existed=True, created=False
        )

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "✓" in call_text
        assert "Config exists" in call_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_directory_status_created(self, mock_echo):
        """Test printing directory status when created."""
        InitOutputFormatter.print_directory_status(
            "/tmp/logs", "Logs directory", existed=False, created=True
        )

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "✅" in call_text
        assert "Logs directory" in call_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_webhook_prompt(self, mock_echo):
        """Test printing webhook installation prompt."""
        InitOutputFormatter.print_webhook_prompt()

        # Should print multiple lines explaining webhook installation
        assert mock_echo.call_count >= 5
        calls_text = " ".join(str(call[0][0]) for call in mock_echo.call_args_list)
        assert "LaunchAgent" in calls_text
        assert "shell config" in calls_text
        assert "dependencies" in calls_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_summary_with_successes(self, mock_echo):
        """Test printing summary with successful initializations."""
        result = InitializationResult()
        result.add_success("Browser capture system")
        result.add_success("Feedback directory")

        InitOutputFormatter.print_summary(result)

        calls_text = " ".join(
            str(call.args[0]) if call.args else "" for call in mock_echo.call_args_list
        )
        assert "Initialization Summary" in calls_text
        assert "✅ Initialized:" in calls_text
        assert "Browser capture system" in calls_text
        assert "Feedback directory" in calls_text
        assert "🎉" in calls_text  # Success message

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_summary_with_skipped(self, mock_echo):
        """Test printing summary with skipped subsystems."""
        result = InitializationResult()
        result.add_skip("Webhook system", "user declined")

        InitOutputFormatter.print_summary(result)

        calls_text = " ".join(
            str(call.args[0]) if call.args else "" for call in mock_echo.call_args_list
        )
        assert "⏭️  Skipped:" in calls_text
        assert "Webhook system" in calls_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_summary_with_failures(self, mock_echo):
        """Test printing summary with failures."""
        result = InitializationResult()
        result.add_failure("Feedback directory", "Permission denied")

        InitOutputFormatter.print_summary(result)

        calls_text = " ".join(
            str(call.args[0]) if call.args else "" for call in mock_echo.call_args_list
        )
        assert "❌ Failed:" in calls_text
        assert "Feedback directory" in calls_text
        assert "Permission denied" in calls_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_summary_mixed_results(self, mock_echo):
        """Test printing summary with mixed results."""
        result = InitializationResult()
        result.add_success("Browser capture")
        result.add_skip("Webhook system", "already installed")
        result.add_failure("Feedback directory", "Error")

        InitOutputFormatter.print_summary(result)

        calls_text = " ".join(
            str(call.args[0]) if call.args else "" for call in mock_echo.call_args_list
        )
        assert "✅ Initialized:" in calls_text
        assert "⏭️  Skipped:" in calls_text
        assert "❌ Failed:" in calls_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_summary_includes_next_steps(self, mock_echo):
        """Test that summary includes next steps for successful initializations."""
        result = InitializationResult()
        result.add_success("Browser capture system")

        InitOutputFormatter.print_summary(result)

        calls_text = " ".join(
            str(call.args[0]) if call.args else "" for call in mock_echo.call_args_list
        )
        assert "Next steps:" in calls_text
        assert "forge browser-capture --help" in calls_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_info(self, mock_echo):
        """Test printing info message."""
        InitOutputFormatter.print_info("This is an info message")

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "ℹ️" in call_text
        assert "This is an info message" in call_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_warning(self, mock_echo):
        """Test printing warning message."""
        InitOutputFormatter.print_warning("This is a warning")

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "⚠️" in call_text
        assert "This is a warning" in call_text

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_error(self, mock_echo):
        """Test printing error message."""
        InitOutputFormatter.print_error("This is an error")

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "❌" in call_text
        assert "This is an error" in call_text
        # Should go to stderr
        assert mock_echo.call_args[1]["err"] is True

    @patch("forge_hooks.common.init_output.click.echo")
    def test_print_success(self, mock_echo):
        """Test printing success message."""
        InitOutputFormatter.print_success("Operation completed")

        mock_echo.assert_called_once()
        call_text = mock_echo.call_args[0][0]
        assert "✅" in call_text
        assert "Operation completed" in call_text

    @patch("forge_hooks.common.init_output.click.confirm")
    def test_confirm_webhook_install_accepted(self, mock_confirm):
        """Test webhook confirmation when user accepts."""
        mock_confirm.return_value = True

        result = InitOutputFormatter.confirm_webhook_install()

        assert result is True
        mock_confirm.assert_called_once_with(
            "   Proceed with webhook installation?", default=True
        )

    @patch("forge_hooks.common.init_output.click.confirm")
    def test_confirm_webhook_install_declined(self, mock_confirm):
        """Test webhook confirmation when user declines."""
        mock_confirm.return_value = False

        result = InitOutputFormatter.confirm_webhook_install()

        assert result is False
