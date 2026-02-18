"""Output formatting for Product Forge initialization process."""

import click

from .init_result import InitializationResult, SubsystemResult


class InitOutputFormatter:
    """Formats initialization results for CLI output.

    Handles all console output during the initialization process, including
    progress indicators, subsystem results, and final summary.

    This class separates presentation logic from business logic, making it
    easier to test initialization without capturing stdout.
    """

    @staticmethod
    def print_header() -> None:
        """Print initialization header."""
        click.echo("🚀 Initializing Product Forge subsystems...\n")

    @staticmethod
    def print_subsystem_start(name: str, emoji: str = "📦") -> None:
        """Print subsystem initialization start message.

        Args:
            name: Subsystem name (e.g., "feedback/learnings directory")
            emoji: Optional emoji icon (default: 📦)
        """
        click.echo(f"{emoji} Setting up {name}...")

    @staticmethod
    def print_subsystem_result(result: SubsystemResult) -> None:
        """Print individual subsystem result.

        Args:
            result: Subsystem initialization result
        """
        if result.is_success():
            # Print success details if available
            if result.details:
                for key, value in result.details.items():
                    click.echo(f"   ✅ {key}: {value}")
            else:
                click.echo(f"   ✅ {result.name} initialized")
            click.echo()  # Blank line after success

        elif result.is_skipped():
            if result.reason:
                click.echo(f"   ⏭️  Skipped: {result.reason}")
            else:
                click.echo(f"   ⏭️  Skipped {result.name}")
            click.echo()

        elif result.is_failed():
            click.echo(f"   ❌ Failed: {result.reason}", err=True)
            click.echo()

    @staticmethod
    def print_config_status(
        config_path: str, existed: bool, created: bool = False
    ) -> None:
        """Print configuration file status.

        Args:
            config_path: Path to config file
            existed: Whether file existed before initialization
            created: Whether file was created during initialization
        """
        if created or not existed:
            click.echo(f"   ✅ Config created: {config_path}")
        else:
            click.echo(f"   ✓ Config exists: {config_path}")

    @staticmethod
    def print_directory_status(
        directory_path: str, description: str, existed: bool, created: bool = False
    ) -> None:
        """Print directory status.

        Args:
            directory_path: Path to directory
            description: Human-readable description (e.g., "Logs directory")
            existed: Whether directory existed before
            created: Whether directory was created
        """
        if created or not existed:
            click.echo(f"   ✅ {description}: {directory_path}")
        else:
            click.echo(f"   ✓ {description}: {directory_path}")

    @staticmethod
    def print_webhook_prompt() -> None:
        """Print webhook installation confirmation prompt details."""
        click.echo("   ℹ️  This installs system-level components (LaunchAgent, shell config)")
        click.echo("\n   This will:")
        click.echo("   - Install dependencies (terminal-notifier, jq)")
        click.echo("   - Create ~/bin/hooks.json")
        click.echo("   - Install LaunchAgent service")
        click.echo("   - Modify shell config (~/.zshrc)")
        click.echo("   - Configure Claude Code hooks\n")

    @staticmethod
    def print_summary(results: InitializationResult) -> None:
        """Print final summary and next steps.

        Args:
            results: Aggregated initialization results
        """
        click.echo("=" * 60)
        click.echo("\n📊 Initialization Summary:\n")

        # Successful initializations
        successful = results.get_successful()
        if successful:
            click.echo("✅ Initialized:")
            for item in successful:
                click.echo(f"   • {item}")
            click.echo()

        # Skipped subsystems
        skipped = results.get_skipped()
        if skipped:
            click.echo("⏭️  Skipped:")
            for item in skipped:
                click.echo(f"   • {item}")
            click.echo()

        # Failed subsystems
        failed = results.get_failed()
        if failed:
            click.echo("❌ Failed:")
            for name, error in failed:
                click.echo(f"   • {name}: {error}")
            click.echo()

        # Next steps
        if results.has_successes():
            click.echo("🎉 Product Forge is ready to use!\n")
            click.echo("Next steps:")
            for step in results.get_next_steps():
                click.echo(f"  • {step}")

    @staticmethod
    def print_separator() -> None:
        """Print a visual separator line."""
        click.echo()

    @staticmethod
    def print_info(message: str) -> None:
        """Print an informational message.

        Args:
            message: Message to display
        """
        click.echo(f"   ℹ️  {message}")

    @staticmethod
    def print_warning(message: str) -> None:
        """Print a warning message.

        Args:
            message: Warning message
        """
        click.echo(f"   ⚠️  {message}")

    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message to stderr.

        Args:
            message: Error message
        """
        click.echo(f"   ❌ {message}", err=True)

    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message.

        Args:
            message: Success message
        """
        click.echo(f"   ✅ {message}")

    @staticmethod
    def confirm_webhook_install() -> bool:
        """Prompt user to confirm webhook installation.

        Returns:
            True if user confirms, False otherwise
        """
        return click.confirm("   Proceed with webhook installation?", default=True)
