"""Browser log capture utility for Chrome DevTools MCP integration."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def get_config_dir() -> Path:
    """Get forge config directory: ~/.claude/forge/config/"""
    config_dir = Path.home() / ".claude" / "forge" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def load_config() -> Dict[str, Any]:
    """Load or create browser-capture.yaml config."""
    config_file = get_config_dir() / "browser-capture.yaml"

    if not config_file.exists():
        # Create default config on first run
        default_config = {
            "output_dir": "~/browser-logs",
            "console": {
                "levels": ["error", "warn", "info", "log"],
                "include_preserved": True,
            },
            "network": {
                "exclude_types": ["image", "font", "stylesheet", "media"],
                "save_errors_separately": True,
                "capture_bodies": False,
            },
            "performance": {
                "enabled": False,
                "duration_seconds": 10,
            },
            "filters": {
                "exclude_urls": ["*.map", "*analytics*", "*tracking*"],
                "exclude_console_patterns": [
                    "Download the React DevTools",
                    "Warning: componentWill*",
                ],
            },
            "output": {
                "create_symlink": True,
                "max_sessions": 50,
            },
        }
        config_file.write_text(yaml.dump(default_config, default_flow_style=False))

    try:
        return yaml.safe_load(config_file.read_text())
    except Exception as e:
        print(f"Warning: Failed to load config: {e}. Using defaults.", file=sys.stderr)
        return {
            "output_dir": "~/browser-logs",
            "console": {"levels": ["error", "warn", "info"], "include_preserved": True},
            "network": {"exclude_types": ["image", "font"], "save_errors_separately": True},
        }


class BrowserLogCapture:
    """
    Orchestrates Chrome DevTools MCP tools for comprehensive log capture.

    Captures console messages, network requests, and performance traces
    from Chromium-based browsers (Dia, Chrome, Edge, etc.) using the
    Chrome DevTools Protocol via MCP.
    """

    def __init__(self, output_dir: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize browser log capture.

        Args:
            output_dir: Custom output directory (overrides config)
            config: Custom config dict (overrides file config)
        """
        # Load config from file or use provided config
        self.config = config if config is not None else load_config()

        # Set output directory (CLI option overrides config)
        if output_dir:
            self.output_dir = Path(output_dir).expanduser()
        else:
            self.output_dir = Path(self.config.get("output_dir", "~/browser-logs")).expanduser()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir: Optional[Path] = None

    def start_session(self, page_description: str = "browser") -> Path:
        """
        Create timestamped session directory.

        Args:
            page_description: Human-readable page description for directory name

        Returns:
            Path to created session directory
        """
        # Create README.md if it doesn't exist
        self._ensure_readme()

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_desc = "".join(c for c in page_description if c.isalnum() or c in ("-", "_"))
        self.session_dir = self.output_dir / "sessions" / f"{timestamp}-{safe_desc}"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Update 'latest' symlink if configured
        if self.config.get("output", {}).get("create_symlink", True):
            latest = self.output_dir / "latest"
            if latest.exists() or latest.is_symlink():
                latest.unlink()
            latest.symlink_to(self.session_dir)

        return self.session_dir

    def _ensure_readme(self) -> None:
        """Create README.md in output directory if it doesn't exist."""
        readme_path = self.output_dir / "README.md"
        if readme_path.exists():
            return

        readme_content = """# Browser Logs Directory

This directory contains captured browser logs from Chrome DevTools MCP integration.

## Directory Structure

```
browser-logs/
├── sessions/                    # All capture sessions
│   └── YYYYMMDD-HHMMSS-{page}/ # Timestamped session directories
│       ├── console-error.log       # Errors only
│       ├── console-warn.log        # Warnings only
│       ├── console-all.log         # All console output
│       ├── network-errors.log      # Failed requests (4xx, 5xx)
│       ├── network-all.log         # All network requests
│       ├── network-detail.json     # Full request/response data
│       └── performance-trace.json.gz  # Performance profile (optional)
├── latest/                      # Symlink to most recent session
└── README.md                    # This file
```

## Quick Start

### Capture All Logs

```bash
forge browser-capture --page "Dashboard" --all
```

### Capture Console Errors Only

```bash
forge browser-capture --console --errors-only
```

### Capture Network Requests

```bash
forge browser-capture --network --exclude-static
```

## Configuration

Config file: `~/.claude/forge/config/browser-capture.yaml`

Edit the config to customize output directory, filters, and capture settings.

## Related Skills

- `/browser-debug` - Comprehensive browser debugging workflow
- `/console-debugging` - Console error analysis
- `/network-inspection` - Network request investigation

## Browser Compatibility

**✅ Supported** (Chromium-based):
- Dia, Chrome, Edge, Brave, Opera, Vivaldi

**❌ Not Supported**:
- Safari, Firefox (different protocols)

For full documentation, see the browser-debug skill: `/browser-debug`
"""
        readme_path.write_text(readme_content)

    def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Chrome DevTools MCP tool via claude CLI.

        Args:
            tool_name: Full MCP tool name
            params: Tool parameters as dict

        Returns:
            Tool result as dict

        Raises:
            RuntimeError: If tool call fails
        """
        try:
            result = subprocess.run(
                ["claude", "mcp", "call", tool_name, json.dumps(params)],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MCP tool call failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse MCP tool output: {e}") from e

    def capture_console_logs(
        self, errors_only: bool = False, include_preserved: bool = True
    ) -> int:
        """
        Capture all console messages with pagination.

        Args:
            errors_only: Only capture errors and warnings
            include_preserved: Include messages from last 3 navigations

        Returns:
            Number of messages captured
        """
        if not self.session_dir:
            raise RuntimeError("Session not started. Call start_session() first.")

        # Determine message types to capture
        if errors_only:
            types = ["error", "warn"]
        else:
            types = self.config.get("console", {}).get(
                "levels", ["error", "warn", "info", "log"]
            )

        # Call MCP tool to list console messages
        params = {
            "pageIdx": 0,
            "pageSize": 1000,  # Capture large batch
            "types": types,
            "includePreservedMessages": include_preserved,
        }

        try:
            result = self._call_mcp_tool(
                "mcp__plugin_product-design_chrome-devtools__list_console_messages",
                params,
            )

            messages = result.get("messages", [])

            # Save messages by level
            errors = []
            warnings = []
            all_messages = []

            for msg in messages:
                level = msg.get("level", "unknown")
                text = msg.get("text", "")
                timestamp = msg.get("timestamp", "")

                # Apply console pattern filters
                exclude_patterns = self.config.get("filters", {}).get(
                    "exclude_console_patterns", []
                )
                if any(pattern in text for pattern in exclude_patterns):
                    continue

                log_line = f"[{timestamp}] [{level.upper()}] {text}\n"
                all_messages.append(log_line)

                if level == "error":
                    errors.append(log_line)
                elif level == "warn":
                    warnings.append(log_line)

            # Write to files
            if errors:
                (self.session_dir / "console-error.log").write_text("".join(errors))
            if warnings:
                (self.session_dir / "console-warn.log").write_text("".join(warnings))
            if all_messages:
                (self.session_dir / "console-all.log").write_text("".join(all_messages))

            return len(messages)

        except Exception as e:
            print(f"Warning: Failed to capture console logs: {e}", file=sys.stderr)
            return 0

    def capture_network_logs(self, exclude_static: bool = True) -> int:
        """
        Capture network requests, excluding static resources.

        Args:
            exclude_static: Exclude static resources (images, fonts, etc.)

        Returns:
            Number of requests captured
        """
        if not self.session_dir:
            raise RuntimeError("Session not started. Call start_session() first.")

        # Determine resource types to exclude
        exclude_types = []
        if exclude_static:
            exclude_types = self.config.get("network", {}).get(
                "exclude_types", ["image", "font", "stylesheet", "media"]
            )

        # Call MCP tool to list network requests
        params = {
            "pageIdx": 0,
            "pageSize": 1000,
            "includePreservedRequests": False,
        }

        try:
            result = self._call_mcp_tool(
                "mcp__plugin_product-design_chrome-devtools__list_network_requests",
                params,
            )

            requests = result.get("requests", [])

            # Filter and categorize requests
            errors = []
            all_requests = []

            for req in requests:
                resource_type = req.get("resourceType", "")

                # Skip excluded types
                if resource_type in exclude_types:
                    continue

                # Apply URL filters
                url = req.get("url", "")
                exclude_urls = self.config.get("filters", {}).get("exclude_urls", [])
                if any(pattern.replace("*", "") in url for pattern in exclude_urls):
                    continue

                method = req.get("method", "")
                status = req.get("status", 0)
                timestamp = req.get("timestamp", "")

                log_line = f"[{timestamp}] {method} {url} - Status: {status} - Type: {resource_type}\n"
                all_requests.append(log_line)

                # Track errors (4xx, 5xx)
                if status >= 400:
                    errors.append(log_line)

            # Write to files
            if self.config.get("network", {}).get("save_errors_separately", True) and errors:
                (self.session_dir / "network-errors.log").write_text("".join(errors))
            if all_requests:
                (self.session_dir / "network-all.log").write_text("".join(all_requests))

            # Save full request data as JSON
            if requests:
                (self.session_dir / "network-detail.json").write_text(
                    json.dumps(requests, indent=2)
                )

            return len(requests)

        except Exception as e:
            print(f"Warning: Failed to capture network logs: {e}", file=sys.stderr)
            return 0

    def capture_performance_trace(self, duration_seconds: Optional[int] = None) -> Optional[Path]:
        """
        Capture performance trace for specified duration.

        Args:
            duration_seconds: Duration in seconds (uses config default if None)

        Returns:
            Path to trace file if successful, None otherwise
        """
        if not self.session_dir:
            raise RuntimeError("Session not started. Call start_session() first.")

        if duration_seconds is None:
            duration_seconds = self.config.get("performance", {}).get("duration_seconds", 10)

        trace_file = self.session_dir / "performance-trace.json.gz"

        try:
            # Start performance trace
            start_params = {
                "reload": False,
                "autoStop": False,
            }
            self._call_mcp_tool(
                "mcp__plugin_product-design_chrome-devtools__performance_start_trace",
                start_params,
            )

            # Wait for specified duration
            import time
            time.sleep(duration_seconds)

            # Stop and save trace
            stop_params = {
                "filePath": str(trace_file),
            }
            self._call_mcp_tool(
                "mcp__plugin_product-design_chrome-devtools__performance_stop_trace",
                stop_params,
            )

            return trace_file if trace_file.exists() else None

        except Exception as e:
            print(f"Warning: Failed to capture performance trace: {e}", file=sys.stderr)
            return None
