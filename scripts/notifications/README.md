# Claude Code tmux Notification System

Native macOS notifications for Claude Code sessions with click-to-navigate support for tmux panes.

## Overview

When Claude Code finishes a task or needs your attention, you'll receive a macOS notification. Clicking the notification takes you directly to the correct tmux pane.

```
┌─────────────────────────────────────────────┐
│  Claude Code - main                         │
│  Claude is done                             │
│  Project: my-project (window: dev)          │
└─────────────────────────────────────────────┘
        │
        │ click
        ▼
┌─────────────────────────────────────────────┐
│  iTerm2 activates                           │
│  tmux switches to main:2.1                  │
└─────────────────────────────────────────────┘
```

## Quick Start

```bash
/tmux-init
```

That's it! The command installs everything automatically.

## Architecture

```
Claude Code Session
        │
        │ Stop/Notification hook
        ▼
┌─────────────────────────────────────────────┐
│  Claude Hooks (settings.json)               │
│  - Calls: forge notify hook <event>        │
│  - Passes tmux location, project info       │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  forge notify hook (Python)                 │
│  - NotificationManager class                │
│  - Formats and sends notification           │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  terminal-notifier                          │
│  - Shows native macOS notification          │
│  - On click: webhook to go-tmux             │
└─────────────────────────────────────────────┘
        │
        │ user clicks
        ▼
┌─────────────────────────────────────────────┐
│  Webhook Service (port 9000)                │
│  - Routes click to: forge tmux go           │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  forge tmux go (Python)                     │
│  - Switches to tmux session:window.pane     │
│  - Activates iTerm2                          │
└─────────────────────────────────────────────┘
```

All components are Python-based forge CLI commands.

## Files

| File | Purpose |
|------|---------|
| `hooks.json` | Webhook configuration (go-tmux only) |
| `com.claude.webhook.plist` | LaunchAgent to run webhook service |
| `tmux-env.sh` | Shell snippet for tmux environment variables |
| `claude-hooks.json` | Claude hooks configuration reference |

**Python CLI Commands:**
- `forge notify hook` - Sends notifications (called by Claude hooks)
- `forge tmux go` - Navigates to tmux location (called by webhook)
- `forge webhook init` - Automated installer
- `forge webhook status` - Check installation status

## Installation Details

The automated installer (`forge webhook init`) handles:

1. **Dependencies** - Installs terminal-notifier, webhook, jq via Homebrew
2. **Configuration** - Creates ~/bin/hooks.json with webhook routing
3. **LaunchAgent** - Sets up com.claude.webhook.plist for auto-start
4. **Shell Environment** - Adds tmux env vars to ~/.zshrc
5. **Claude Hooks** - Configures hooks to call `forge notify hook`

All notification logic is implemented in Python (NotificationManager class) rather than bash scripts.

## Commands

```bash
/tmux-init              # Install notification system
/tmux-init --status     # Check installation status
/tmux-init --uninstall  # Remove notification system

# Or use forge CLI directly:
forge webhook init      # Install notification system
forge webhook status    # Check installation status
forge notify hook Stop  # Test notification
forge tmux go "main:0.0"  # Test navigation
```

## Customization

### Change Terminal

Edit `src/forge_hooks/utils/tmux.py` in the `TmuxManager.activate_terminal()` method to use a different terminal application.

### Change Notification Sound or Style

Edit `src/forge_hooks/utils/notification.py` in the `NotificationManager.send()` method to customize notification appearance and sound.

### Change Webhook Port

1. Edit `com.claude.webhook.plist` to change the port
2. Update `hooks.json` if needed
3. No need to update notification code - webhook URL is generated automatically

## Troubleshooting

### Check Status

```bash
forge webhook status
# or
/tmux-init --status
```

### View Logs

```bash
tail -f ~/Library/Logs/claude-webhook/webhook.log
tail -f ~/Library/Logs/claude-webhook/webhook.error.log
```

### Test Notification

```bash
# Test with Python CLI
forge notify hook Stop

# Or test webhook directly (legacy)
curl -X POST -H "Content-Type: application/json" \
  -d '{"tmux_location":"main:0.0","tmux_session_name":"main","tmux_window_name":"dev","project":"test","cwd":"/tmp","hook_event_name":"Stop","session_id":"test"}' \
  http://localhost:9000/hooks/claude-notify
```

### Restart Webhook Service

```bash
launchctl unload ~/Library/LaunchAgents/com.claude.webhook.plist
launchctl load ~/Library/LaunchAgents/com.claude.webhook.plist
```

### Port Already in Use

```bash
# Find what's using port 9000
lsof -i :9000

# Kill it if needed
kill -9 <PID>
```

## Credits

Based on [Claude Code Notification System for Tmux](https://quemy.info/2025-08-04-notification-system-tmux-claude.html) by Quemy.
