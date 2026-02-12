"""Install and manage Claude Code webhook notification system."""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from ..common.logging_config import setup_logging

logger = setup_logging()


class WebhookInstaller:
    """Install and manage Claude Code webhook notification system."""

    def __init__(self):
        """Initialize WebhookInstaller with paths."""
        self.scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts" / "notifications"
        self.bin_dir = Path.home() / "bin"
        self.launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        self.plist_name = "com.claude.webhook.plist"
        self.claude_settings = Path.home() / ".claude" / "settings.json"
        self.log_dir = Path.home() / "Library" / "Logs" / "claude-webhook"

        logger.debug(f"Initialized WebhookInstaller with scripts_dir={self.scripts_dir}")

    def check_dependencies(self) -> dict[str, bool]:
        """
        Check if required dependencies are installed.

        Returns:
            Dictionary mapping dependency name to installed status
        """
        dependencies = ["terminal-notifier", "webhook", "jq"]
        status = {}

        for dep in dependencies:
            path = shutil.which(dep)
            status[dep] = path is not None
            logger.debug(f"Dependency {dep}: {'installed' if status[dep] else 'not found'}")

        return status

    def install_dependencies(self) -> None:
        """
        Install missing dependencies via Homebrew.

        Raises:
            RuntimeError: If Homebrew is not available or installation fails
        """
        # Check if brew is available
        if not shutil.which("brew"):
            raise RuntimeError(
                "Homebrew not found. Install from https://brew.sh/ or install dependencies manually."
            )

        # Install all required dependencies
        dependencies = ["terminal-notifier", "webhook", "jq"]

        logger.info(f"Installing dependencies: {', '.join(dependencies)}")

        try:
            result = subprocess.run(
                ["brew", "install"] + dependencies,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode != 0:
                logger.error(f"Homebrew install failed: {result.stderr}")
                raise RuntimeError(f"Failed to install dependencies: {result.stderr}")

            logger.info("Dependencies installed successfully")

        except subprocess.TimeoutExpired:
            logger.error("Homebrew install timed out")
            raise RuntimeError("Dependency installation timed out (>5 minutes)")
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            raise

    def ensure_scripts_executable(self) -> None:
        """
        Ensure forge command is available.

        Forge CLI commands used:
        - 'forge notify hook': Called directly by Claude Code hooks
        - 'forge tmux go': Called by go-tmux webhook (notification click actions)

        Raises:
            RuntimeError: If forge command is not found
        """
        # Check that forge command is available
        if not shutil.which("forge"):
            raise RuntimeError(
                "forge command not found in PATH. "
                "Ensure forge is installed and accessible."
            )

        logger.info("Forge CLI ready for notifications and tmux navigation")

    def create_hooks_json(self) -> None:
        """
        Create hooks.json with proper paths.

        Webhook configuration:
        - go-tmux: 'forge tmux go' (handles notification click actions)

        Note: Notifications are sent directly by Claude Code hooks via
        'forge notify hook' - no webhook needed for notifications.

        Raises:
            RuntimeError: If hooks.json creation fails
        """
        src = self.scripts_dir / "hooks.json"
        dst = self.bin_dir / "hooks.json"

        if not src.exists():
            raise RuntimeError(f"Source hooks.json not found: {src}")

        # Find forge binary
        forge_bin = shutil.which("forge")
        if not forge_bin:
            raise RuntimeError(
                "forge command not found in PATH. "
                "Ensure forge is installed and accessible."
            )

        # Ensure bin directory exists for hooks.json only
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating hooks.json in {self.bin_dir}")

        # Read template
        content = src.read_text()

        # Replace placeholders
        content = content.replace("__FORGE_BIN__", forge_bin)

        # Write to destination
        dst.write_text(content)
        logger.debug(
            f"hooks.json created: go-tmux webhook uses '{forge_bin} tmux go' "
            "(notifications sent directly via 'forge notify hook')"
        )

    def install_launchagent(self) -> None:
        """
        Install webhook LaunchAgent.

        Raises:
            RuntimeError: If LaunchAgent installation fails
        """
        # Ensure launch agents directory exists
        self.launch_agents_dir.mkdir(parents=True, exist_ok=True)

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        src = self.scripts_dir / self.plist_name
        dst = self.launch_agents_dir / self.plist_name

        if not src.exists():
            raise RuntimeError(f"Source plist not found: {src}")

        logger.info(f"Installing LaunchAgent to {dst}")

        # Find webhook binary
        webhook_bin = shutil.which("webhook")
        if not webhook_bin:
            raise RuntimeError("webhook binary not found. Install with: brew install webhook")

        # Read template
        content = src.read_text()

        # Replace placeholders
        content = content.replace("__WEBHOOK_BIN__", webhook_bin)
        content = content.replace("__HOOKS_JSON__", str(self.bin_dir / "hooks.json"))
        content = content.replace("__LOG_DIR__", str(self.log_dir))

        # Write to destination
        dst.write_text(content)
        logger.debug("LaunchAgent plist created with proper paths")

        # Unload existing agent if loaded
        try:
            subprocess.run(
                ["launchctl", "unload", str(dst)],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception:
            pass  # It's ok if it wasn't loaded

        # Load the LaunchAgent
        try:
            result = subprocess.run(
                ["launchctl", "load", str(dst)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.warning(f"launchctl load warning: {result.stderr}")
                # Don't raise, as it might still work

            logger.info("LaunchAgent loaded successfully")

        except subprocess.TimeoutExpired:
            logger.error("launchctl load timed out")
            raise RuntimeError("Failed to load LaunchAgent (timeout)")
        except Exception as e:
            logger.error(f"Error loading LaunchAgent: {e}")
            raise RuntimeError(f"Failed to load LaunchAgent: {e}")

    def setup_shell_env(self) -> None:
        """
        Add tmux environment setup to shell config.

        Adds tmux-env.sh content to ~/.zshrc if not already present.
        """
        zshrc = Path.home() / ".zshrc"
        tmux_env_src = self.scripts_dir / "tmux-env.sh"

        if not tmux_env_src.exists():
            raise RuntimeError(f"Source tmux-env.sh not found: {tmux_env_src}")

        logger.info("Configuring shell environment")

        # Read tmux env content
        tmux_env_content = tmux_env_src.read_text()

        # Check if already in .zshrc
        if zshrc.exists():
            zshrc_content = zshrc.read_text()
            if "WS_TMUX_LOCATION" in zshrc_content:
                logger.info("Shell environment already configured (found WS_TMUX_LOCATION)")
                return

        # Append to .zshrc
        with zshrc.open("a") as f:
            f.write("\n# Claude Code tmux notification environment\n")
            f.write(tmux_env_content)
            if not tmux_env_content.endswith("\n"):
                f.write("\n")

        logger.info("Shell environment configured. Run: source ~/.zshrc")

    def configure_claude_hooks(self) -> None:
        """
        Add hooks to Claude settings.json.

        Merges hooks from claude-hooks.json into ~/.claude/settings.json,
        preserving existing hooks.

        Raises:
            RuntimeError: If Claude settings configuration fails
        """
        claude_hooks_src = self.scripts_dir / "claude-hooks.json"

        if not claude_hooks_src.exists():
            raise RuntimeError(f"Source claude-hooks.json not found: {claude_hooks_src}")

        logger.info("Configuring Claude Code hooks")

        # Read hook templates
        hook_templates = json.loads(claude_hooks_src.read_text())
        new_hooks = hook_templates.get("hooks", {})

        # Ensure settings file exists
        self.claude_settings.parent.mkdir(parents=True, exist_ok=True)
        if not self.claude_settings.exists():
            settings = {}
        else:
            try:
                settings = json.loads(self.claude_settings.read_text())
            except json.JSONDecodeError:
                logger.warning("Could not parse existing settings.json, starting fresh")
                settings = {}

        # Merge hooks
        if "hooks" not in settings:
            settings["hooks"] = {}

        for hook_name, hook_entries in new_hooks.items():
            settings["hooks"][hook_name] = hook_entries
            logger.debug(f"Added/updated {hook_name} hook")

        # Write back
        self.claude_settings.write_text(json.dumps(settings, indent=2) + "\n")
        logger.info("Claude hooks configured successfully")

    def check_status(self) -> dict[str, Any]:
        """
        Check installation status of all components.

        Returns:
            Dictionary with status of each component
        """
        status: dict[str, Any] = {}

        # Check dependencies
        status["dependencies"] = self.check_dependencies()
        status["dependencies_installed"] = all(status["dependencies"].values())

        # Check forge CLI availability and hooks.json (in ~/bin)
        hooks_json = self.bin_dir / "hooks.json"

        # Check that forge command is available (for both 'forge tmux go' and 'forge notify send')
        forge_available = shutil.which("forge") is not None

        status["forge_cli_available"] = forge_available
        status["hooks_json_configured"] = hooks_json.exists()

        # Check LaunchAgent
        plist_file = self.launch_agents_dir / self.plist_name
        status["launchagent_installed"] = plist_file.exists()

        # Check if LaunchAgent is loaded
        try:
            result = subprocess.run(
                ["launchctl", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            status["launchagent_loaded"] = "com.claude.webhook" in result.stdout
        except Exception:
            status["launchagent_loaded"] = False

        # Check Claude hooks
        status["claude_hooks_configured"] = False
        if self.claude_settings.exists():
            try:
                settings = json.loads(self.claude_settings.read_text())
                hooks = settings.get("hooks", {})
                status["claude_hooks_configured"] = "Stop" in hooks or "Notification" in hooks
            except Exception:
                pass

        # Check shell configuration
        zshrc = Path.home() / ".zshrc"
        status["shell_configured"] = False
        if zshrc.exists():
            zshrc_content = zshrc.read_text()
            status["shell_configured"] = "WS_TMUX_LOCATION" in zshrc_content

        # Overall status
        status["installed"] = (
            status["dependencies_installed"]
            and status["forge_cli_available"]
            and status["hooks_json_configured"]
            and status["launchagent_installed"]
            and status["launchagent_loaded"]
            and status["claude_hooks_configured"]
            and status["shell_configured"]
        )

        return status

    def uninstall(self) -> None:
        """
        Remove webhook notification system.

        This is a placeholder for future implementation.
        """
        logger.info("Uninstall functionality not yet implemented")
        raise NotImplementedError("Uninstall functionality coming soon")
