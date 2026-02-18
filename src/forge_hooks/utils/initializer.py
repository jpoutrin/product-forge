"""Orchestrator for Product Forge subsystem initialization."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..common.init_output import InitOutputFormatter
from ..common.init_result import InitializationResult, SubsystemResult


class InitializerOrchestrator:
    """Orchestrates Product Forge subsystem initialization.

    Coordinates the initialization of feedback, browser capture, and webhook
    subsystems, aggregating results and handling errors consistently.

    This class follows the same pattern as WebhookInstaller and BrowserLogCapture,
    providing a high-level interface for the CLI while delegating to specialized
    classes for actual implementation.

    Example:
        >>> orchestrator = InitializerOrchestrator()
        >>> results = orchestrator.initialize_all(skip_webhook=True)
        >>> if results.has_failures():
        ...     print("Some subsystems failed")
    """

    def __init__(
        self,
        formatter: Optional[InitOutputFormatter] = None,
    ):
        """Initialize orchestrator.

        Args:
            formatter: Output formatter (default: InitOutputFormatter)
        """
        self.formatter = formatter or InitOutputFormatter()

    def initialize_all(
        self,
        skip_feedback: bool = False,
        skip_browser: bool = False,
        skip_webhook: bool = False,
        force: bool = False,
    ) -> InitializationResult:
        """Initialize all non-skipped subsystems.

        Args:
            skip_feedback: Skip feedback/learnings directory setup
            skip_browser: Skip browser capture system setup
            skip_webhook: Skip webhook notification system setup
            force: Force reinstall even if already installed

        Returns:
            InitializationResult with aggregated status
        """
        results = InitializationResult()

        # 1. Initialize feedback/learnings directory
        if not skip_feedback:
            self.formatter.print_subsystem_start("feedback/learnings directory", emoji="📚")
            result = self._init_feedback(force=force)
            self.formatter.print_subsystem_result(result)
            if result.is_success():
                results.add_success(result.name, result.details)
            elif result.is_skipped():
                results.add_skip(result.name, result.reason or "skipped")
            else:
                results.add_failure(result.name, result.reason or "unknown error")
        else:
            results.add_skip("Feedback directory", "skipped by user")

        # 2. Initialize browser capture system
        if not skip_browser:
            self.formatter.print_subsystem_start("browser capture system", emoji="🌐")
            result = self._init_browser_capture(force=force)
            self.formatter.print_subsystem_result(result)
            if result.is_success():
                results.add_success(result.name, result.details)
            elif result.is_skipped():
                results.add_skip(result.name, result.reason or "skipped")
            else:
                results.add_failure(result.name, result.reason or "unknown error")
        else:
            results.add_skip("Browser capture", "skipped by user")

        # 3. Initialize webhook notification system
        if not skip_webhook:
            self.formatter.print_subsystem_start("webhook notification system", emoji="🔔")
            result = self._init_webhook(force=force)
            self.formatter.print_subsystem_result(result)
            if result.is_success():
                results.add_success(result.name, result.details)
            elif result.is_skipped():
                results.add_skip(result.name, result.reason or "skipped")
            else:
                results.add_failure(result.name, result.reason or "unknown error")
        else:
            results.add_skip("Webhook system", "skipped by user")

        return results

    def _init_feedback(self, force: bool) -> SubsystemResult:
        """Initialize feedback/learnings directory.

        Args:
            force: Force reinstall

        Returns:
            SubsystemResult with initialization status
        """
        try:
            # Call forge feedback init via subprocess
            result = subprocess.run(
                ["forge", "feedback", "init"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return SubsystemResult(
                    name="Feedback/learnings directory",
                    status="success",
                    details={"initialized": "Feedback directory initialized"},
                )
            else:
                return SubsystemResult(
                    name="Feedback/learnings directory",
                    status="failed",
                    reason=result.stderr.strip() or "initialization failed",
                )

        except subprocess.TimeoutExpired:
            return SubsystemResult(
                name="Feedback/learnings directory",
                status="failed",
                reason="initialization timed out",
            )
        except Exception as e:
            return SubsystemResult(
                name="Feedback/learnings directory",
                status="failed",
                reason=str(e),
            )

    def _init_browser_capture(self, force: bool) -> SubsystemResult:
        """Initialize browser capture system.

        Args:
            force: Force reinstall

        Returns:
            SubsystemResult with initialization status
        """
        try:
            from .browser_capture import BrowserLogCapture, get_config_dir

            # Initialize config (auto-creates if missing)
            config_file = get_config_dir() / "browser-capture.yaml"
            config_existed = config_file.exists()

            # Initialize browser logs directory
            capture = BrowserLogCapture()
            readme_existed = (capture.output_dir / "README.md").exists()

            # Create initial session to ensure all directories exist
            session_dir = capture.start_session(page_description="init-test")

            # Build details dict for output
            details = {}

            if not config_existed:
                details["Config created"] = str(config_file)
            else:
                details["Config exists"] = str(config_file)

            if not readme_existed:
                details["README created"] = str(capture.output_dir / "README.md")
            else:
                details["README exists"] = str(capture.output_dir / "README.md")

            details["Logs directory"] = str(capture.output_dir)
            details["Test session"] = str(session_dir)

            return SubsystemResult(
                name="Browser capture system",
                status="success",
                details=details,
            )

        except Exception as e:
            return SubsystemResult(
                name="Browser capture system",
                status="failed",
                reason=str(e),
            )

    def _init_webhook(self, force: bool) -> SubsystemResult:
        """Initialize webhook notification system with user confirmation.

        Args:
            force: Force reinstall without confirmation

        Returns:
            SubsystemResult with initialization status
        """
        self.formatter.print_info(
            "This installs system-level components (LaunchAgent, shell config)"
        )

        try:
            from .webhook import WebhookInstaller

            installer = WebhookInstaller()
            status = installer.check_status()

            # Check if already installed
            if status["installed"] and not force:
                return SubsystemResult(
                    name="Webhook notification system",
                    status="skipped",
                    reason="already installed (use --force to reinstall)",
                )

            # Show installation details and confirm
            if not force:
                self.formatter.print_webhook_prompt()

                if not self.formatter.confirm_webhook_install():
                    return SubsystemResult(
                        name="Webhook notification system",
                        status="skipped",
                        reason="user declined",
                    )

            # Run forge webhook init
            args = ["forge", "webhook", "init"]
            if force:
                args.append("--force")

            result = subprocess.run(
                args,
                capture_output=False,  # Show interactive output
                timeout=60,
            )

            if result.returncode == 0:
                return SubsystemResult(
                    name="Webhook notification system",
                    status="success",
                    details={"installed": "Webhook system installed"},
                )
            else:
                return SubsystemResult(
                    name="Webhook notification system",
                    status="failed",
                    reason="installation failed",
                )

        except ImportError:
            return SubsystemResult(
                name="Webhook notification system",
                status="skipped",
                reason="not available (missing dependencies)",
            )
        except subprocess.TimeoutExpired:
            return SubsystemResult(
                name="Webhook notification system",
                status="failed",
                reason="installation timed out",
            )
        except Exception as e:
            return SubsystemResult(
                name="Webhook notification system",
                status="failed",
                reason=str(e),
            )
