---
name: tmux-init
description: Set up tmux notification system for Claude Code sessions
argument-hint: "[--uninstall] [--status]"
allowed-tools: Bash, Read, Write, Edit
---

# tmux-init

Set up a notification system for Claude Code that sends native macOS notifications when sessions need attention, with click-to-navigate support for tmux panes.

## Usage

```bash
/tmux-init              # Install notification system
/tmux-init --status     # Check installation status
/tmux-init --uninstall  # Remove notification system
```

## What Gets Installed

1. **Configuration** in `~/bin/`:
   - `hooks.json` - Webhook routing configuration

2. **Webhook service** (LaunchAgent):
   - Listens on port 9000 for notification requests
   - Auto-starts on login

3. **Shell environment** (added to ~/.zshrc):
   - `WS_TMUX_LOCATION` - Current tmux session:window.pane
   - `WS_TMUX_SESSION_NAME` - Current session name
   - `WS_TMUX_WINDOW_NAME` - Current window name

4. **Claude hooks** (added to ~/.claude/settings.json):
   - `Stop` hook - Calls `forge notify hook` when Claude finishes
   - `Notification` hook - Calls `forge notify hook` when Claude needs input

5. **Python CLI commands**:
   - `forge notify hook` - Sends notifications (called by Claude hooks)
   - `forge tmux go` - Navigates to tmux location (called by webhook on click)

## Prerequisites

- macOS
- tmux
- Homebrew (for installing dependencies)

## Execution Instructions

### Parse Arguments

```bash
UNINSTALL=false
STATUS=false

for arg in "$@"; do
    case "$arg" in
        --uninstall) UNINSTALL=true ;;
        --status) STATUS=true ;;
    esac
done
```

### If --status: Check Installation Status

```bash
echo "=== Claude tmux Notification System Status ==="
echo ""

# Check dependencies
echo "Dependencies:"
command -v terminal-notifier &>/dev/null && echo "  ✅ terminal-notifier" || echo "  ❌ terminal-notifier (missing)"
command -v webhook &>/dev/null && echo "  ✅ webhook" || echo "  ❌ webhook (missing)"
command -v jq &>/dev/null && echo "  ✅ jq" || echo "  ❌ jq (missing)"
command -v tmux &>/dev/null && echo "  ✅ tmux" || echo "  ❌ tmux (missing)"
echo ""

# Check configuration and CLI commands
echo "Configuration:"
[ -f "$HOME/bin/hooks.json" ] && echo "  ✅ ~/bin/hooks.json" || echo "  ❌ ~/bin/hooks.json (missing)"
command -v forge &>/dev/null && echo "  ✅ forge CLI" || echo "  ❌ forge CLI (missing)"
forge notify hook --help &>/dev/null && echo "  ✅ forge notify hook" || echo "  ❌ forge notify hook (missing)"
forge tmux go --help &>/dev/null && echo "  ✅ forge tmux go" || echo "  ❌ forge tmux go (missing)"
echo ""

# Check LaunchAgent
echo "Webhook Service:"
PLIST="$HOME/Library/LaunchAgents/com.claude.webhook.plist"
if [ -f "$PLIST" ]; then
    if launchctl list | grep -q "com.claude.webhook"; then
        echo "  ✅ LaunchAgent installed and running"
    else
        echo "  ⚠️  LaunchAgent installed but not running"
    fi
else
    echo "  ❌ LaunchAgent not installed"
fi
echo ""

# Check webhook port
echo "Webhook Port:"
if curl -s http://localhost:9000/hooks/claude-notify -o /dev/null -w "%{http_code}" | grep -q "200\|405"; then
    echo "  ✅ Port 9000 responding"
else
    echo "  ❌ Port 9000 not responding"
fi
echo ""

# Check shell environment
echo "Shell Environment:"
if grep -q "WS_TMUX_LOCATION" "$HOME/.zshrc" 2>/dev/null; then
    echo "  ✅ tmux env vars in ~/.zshrc"
else
    echo "  ❌ tmux env vars not in ~/.zshrc"
fi
echo ""

# Check Claude hooks via webhook log
echo "Claude Hooks (check log for activity):"
LOG_FILE="$HOME/Library/Logs/claude-webhook/webhook.log"
if [ -f "$LOG_FILE" ]; then
    RECENT_LINES=$(tail -5 "$LOG_FILE" 2>/dev/null)
    if [ -n "$RECENT_LINES" ]; then
        echo "  Recent webhook log entries:"
        echo "$RECENT_LINES" | sed 's/^/    /'
    else
        echo "  ⚠️  Log file exists but is empty"
    fi
    echo ""
    echo "  To verify hooks are working, trigger a Claude stop event"
    echo "  and check: tail -f ~/Library/Logs/claude-webhook/webhook.log"
else
    echo "  ⚠️  No log file yet at ~/Library/Logs/claude-webhook/webhook.log"
    echo "  Log will be created when first notification is received"
fi
```

Exit after showing status.

### If --uninstall: Remove Installation

```bash
echo "=== Uninstalling Claude tmux Notification System ==="
echo ""

# Stop and remove LaunchAgent
PLIST="$HOME/Library/LaunchAgents/com.claude.webhook.plist"
if [ -f "$PLIST" ]; then
    echo "Stopping webhook service..."
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "  ✅ LaunchAgent removed"
fi

# Remove configuration
echo "Removing configuration..."
rm -f "$HOME/bin/hooks.json"
echo "  ✅ Configuration removed"

# Note: Don't remove shell env or Claude hooks automatically
echo ""
echo "Manual cleanup (optional):"
echo "  - Remove WS_TMUX_* lines from ~/.zshrc"
echo "  - Remove Stop/Notification hooks from ~/.claude/settings.json"
echo ""
echo "✅ Uninstallation complete"
```

Exit after uninstalling.

### Install: Full Setup

Run the automated installer:

```bash
forge webhook init
```

This command will:
1. Install dependencies (terminal-notifier, webhook, jq)
2. Create webhook configuration (~/bin/hooks.json)
3. Set up LaunchAgent for webhook service
4. Configure Claude Code hooks to call `forge notify hook`
5. Set up shell environment (tmux env vars)

After installation:
```bash
# Check status
forge webhook status

# Restart your shell
source ~/.zshrc

# Start a new tmux session and run Claude Code
# You'll receive notifications when Claude finishes or needs input
```

## Troubleshooting

### Notifications not appearing

1. Check if webhook is running:
   ```bash
   launchctl list | grep claude.webhook
   ```

2. Check webhook logs:
   ```bash
   tail -f ~/Library/Logs/claude-webhook/webhook.log
   ```

3. Test webhook manually:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"tmux_location":"test:0.0","hook_event_name":"Stop"}' \
     http://localhost:9000/hooks/claude-notify
   ```

### Click doesn't navigate to pane

1. Ensure tmux env vars are set:
   ```bash
   echo $WS_TMUX_LOCATION
   ```

2. Test navigation command:
   ```bash
   forge tmux go "session:0.0"
   ```

### Webhook won't start

1. Check if port 9000 is in use:
   ```bash
   lsof -i :9000
   ```

2. Try restarting:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.claude.webhook.plist
   launchctl load ~/Library/LaunchAgents/com.claude.webhook.plist
   ```
