"""Tests for initialization result tracking."""

import pytest

from forge_hooks.common.init_result import InitializationResult, SubsystemResult


class TestSubsystemResult:
    """Tests for SubsystemResult dataclass."""

    def test_create_success_result(self):
        """Test creating a successful result."""
        result = SubsystemResult(
            name="Browser capture",
            status="success",
            details={"config": "~/.claude/forge/config/browser-capture.yaml"},
        )

        assert result.name == "Browser capture"
        assert result.status == "success"
        assert result.is_success()
        assert not result.is_skipped()
        assert not result.is_failed()
        assert result.details["config"] == "~/.claude/forge/config/browser-capture.yaml"

    def test_create_skipped_result(self):
        """Test creating a skipped result."""
        result = SubsystemResult(
            name="Webhook system", status="skipped", reason="already installed"
        )

        assert result.name == "Webhook system"
        assert result.status == "skipped"
        assert result.reason == "already installed"
        assert result.is_skipped()
        assert not result.is_success()
        assert not result.is_failed()

    def test_create_failed_result(self):
        """Test creating a failed result."""
        result = SubsystemResult(
            name="Feedback directory",
            status="failed",
            reason="Permission denied: /tmp/learnings",
        )

        assert result.name == "Feedback directory"
        assert result.status == "failed"
        assert result.reason == "Permission denied: /tmp/learnings"
        assert result.is_failed()
        assert not result.is_success()
        assert not result.is_skipped()

    def test_result_without_reason_or_details(self):
        """Test creating result without optional fields."""
        result = SubsystemResult(name="Test subsystem", status="success")

        assert result.reason is None
        assert result.details is None


class TestInitializationResult:
    """Tests for InitializationResult aggregator."""

    def test_empty_result(self):
        """Test newly created result is empty."""
        result = InitializationResult()

        assert len(result) == 0
        assert not result  # __bool__ returns False when empty
        assert not result.has_failures()
        assert not result.has_successes()
        assert result.get_successful() == []
        assert result.get_skipped() == []
        assert result.get_failed() == []

    def test_add_success(self):
        """Test adding successful subsystem."""
        result = InitializationResult()
        result.add_success("Browser capture", details={"path": "/tmp/logs"})

        assert len(result) == 1
        assert result.has_successes()
        assert not result.has_failures()
        assert result.get_successful() == ["Browser capture"]

    def test_add_skip(self):
        """Test adding skipped subsystem."""
        result = InitializationResult()
        result.add_skip("Webhook system", "user declined")

        assert len(result) == 1
        assert not result.has_successes()
        assert not result.has_failures()
        assert result.get_skipped() == ["Webhook system (user declined)"]

    def test_add_failure(self):
        """Test adding failed subsystem."""
        result = InitializationResult()
        result.add_failure("Feedback directory", "Permission denied")

        assert len(result) == 1
        assert not result.has_successes()
        assert result.has_failures()
        assert result.get_failed() == [("Feedback directory", "Permission denied")]

    def test_mixed_results(self):
        """Test aggregating mixed success/skip/failure results."""
        result = InitializationResult()
        result.add_success("Browser capture")
        result.add_skip("Webhook system", "already installed")
        result.add_failure("Feedback directory", "Error: missing dependency")

        assert len(result) == 3
        assert result.has_successes()
        assert result.has_failures()
        assert result.get_successful() == ["Browser capture"]
        assert result.get_skipped() == ["Webhook system (already installed)"]
        assert result.get_failed() == [("Feedback directory", "Error: missing dependency")]

    def test_get_next_steps_browser_only(self):
        """Test next steps when only browser capture initialized."""
        result = InitializationResult()
        result.add_success("Browser capture system")

        steps = result.get_next_steps()

        assert "Test browser capture: forge browser-capture --help" in steps
        assert "Run 'forge --help' to see all available commands" in steps
        assert len(steps) == 2

    def test_get_next_steps_feedback_only(self):
        """Test next steps when only feedback initialized."""
        result = InitializationResult()
        result.add_success("Feedback/learnings directory")

        steps = result.get_next_steps()

        assert "View feedback: forge feedback list" in steps
        assert "Run 'forge --help' to see all available commands" in steps

    def test_get_next_steps_webhook_only(self):
        """Test next steps when only webhook initialized."""
        result = InitializationResult()
        result.add_success("Webhook notification system")

        steps = result.get_next_steps()

        assert "Restart your shell: source ~/.zshrc" in steps
        assert "Start Claude Code in tmux for notifications" in steps
        assert "Run 'forge --help' to see all available commands" in steps

    def test_get_next_steps_all_systems(self):
        """Test next steps when all systems initialized."""
        result = InitializationResult()
        result.add_success("Browser capture system")
        result.add_success("Feedback/learnings directory")
        result.add_success("Webhook notification system")

        steps = result.get_next_steps()

        # Should include steps for all systems
        assert len(steps) == 5
        assert any("browser" in step.lower() for step in steps)
        assert any("feedback" in step.lower() for step in steps)
        assert any("shell" in step.lower() for step in steps)

    def test_get_next_steps_no_successes(self):
        """Test next steps when nothing succeeded."""
        result = InitializationResult()
        result.add_skip("Browser capture", "skipped by user")
        result.add_failure("Webhook", "error")

        steps = result.get_next_steps()

        assert steps == []

    def test_skip_without_reason(self):
        """Test skipped result without reason displays correctly."""
        result = InitializationResult()
        # This shouldn't happen in practice, but handle gracefully
        result.results.append(SubsystemResult(name="Test", status="skipped", reason=None))

        skipped = result.get_skipped()

        assert skipped == ["Test"]

    def test_failed_without_reason(self):
        """Test failed result without reason uses default."""
        result = InitializationResult()
        result.results.append(SubsystemResult(name="Test", status="failed", reason=None))

        failed = result.get_failed()

        assert failed == [("Test", "unknown error")]

    def test_bool_conversion(self):
        """Test boolean conversion of result."""
        result = InitializationResult()

        assert not result  # Empty result is falsy

        result.add_success("Test")

        assert result  # Non-empty result is truthy
