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
│  - Captures tmux location, project info     │
│  - Sends JSON to localhost:9000             │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  Webhook Service (port 9000)                │
│  - Receives notification requests           │
│  - Executes notify-claude.sh                │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  terminal-notifier                          │
│  - Shows native macOS notification          │
│  - On click: calls go-tmux.sh               │
└─────────────────────────────────────────────┘
        │
        │ user clicks
        ▼
┌─────────────────────────────────────────────┐
│  go-tmux.sh                                 │
│  - Switches to tmux session:window.pane    │
│  - Activates iTerm2                         │
└─────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `notify-claude.sh` | Generates macOS notification with terminal-notifier |
| `go-tmux.sh` | Navigates to tmux pane and activates terminal |
| `hooks.json` | Webhook configuration for routing requests |
| `com.claude.webhook.plist` | LaunchAgent to run webhook service |
| `tmux-env.sh` | Shell snippet for tmux environment variables |
| `claude-hooks.json` | Claude hooks configuration reference |

## Manual Installation

If you prefer to install manually:

### 1. Install Dependencies

```bash
brew install terminal-notifier webhook jq
```

### 2. Copy Scripts

```bash
mkdir -p ~/bin
cp notify-claude.sh go-tmux.sh ~/bin/
chmod +x ~/bin/notify-claude.sh ~/bin/go-tmux.sh

# Update hooks.json with your path
sed 's|__BIN_DIR__|'"$HOME/bin"'|g' hooks.json > ~/bin/hooks.json
```

### 3. Set Up LaunchAgent

```bash
# Update plist with your paths
sed -e 's|__WEBHOOK_BIN__|'$(which webhook)'|g' \
    -e 's|__HOOKS_JSON__|'"$HOME/bin/hooks.json"'|g' \
    -e 's|__LOG_DIR__|'"$HOME/Library/Logs/claude-webhook"'|g' \
    com.claude.webhook.plist > ~/Library/LaunchAgents/com.claude.webhook.plist

mkdir -p ~/Library/Logs/claude-webhook
launchctl load ~/Library/LaunchAgents/com.claude.webhook.plist
```

### 4. Add to ~/.zshrc

```bash
cat tmux-env.sh >> ~/.zshrc
source ~/.zshrc
```

### 5. Configure Claude Hooks

Add the hooks from `claude-hooks.json` to `~/.claude/settings.json`.

## Commands

```bash
/tmux-init              # Install notification system
/tmux-init --status     # Check installation status
/tmux-init --uninstall  # Remove notification system
```

## Customization

### Change Terminal

Edit `go-tmux.sh` to use a different terminal:

```bash
# For Ghostty:
osascript -e 'tell application "Ghostty" to activate'

# For Alacritty:
osascript -e 'tell application "Alacritty" to activate'

# For Terminal.app:
osascript -e 'tell application "Terminal" to activate'
```

### Change Notification Sound

Edit `notify-claude.sh`:

```bash
# Available sounds: Basso, Blow, Bottle, Frog, Funk, Glass, Hero,
# Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink
-sound "Glass"
```

### Change Webhook Port

1. Edit `com.claude.webhook.plist`:
   ```xml
   <string>9001</string>  <!-- Change from 9000 -->
   ```

2. Update Claude hooks in `~/.claude/settings.json`:
   ```
   http://localhost:9001/hooks/claude-notify
   ```

3. Update `notify-claude.sh`:
   ```bash
   http://localhost:9001/hooks/go-tmux
   ```

## Troubleshooting

### Check Status

```bash
/tmux-init --status
```

### View Logs

```bash
tail -f ~/Library/Logs/claude-webhook/webhook.log
tail -f ~/Library/Logs/claude-webhook/webhook.error.log
```

### Test Notification

```bash
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
