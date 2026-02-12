#!/bin/zsh
# go-tmux.sh - Navigate to specific tmux pane and activate terminal
#
# Called when user clicks on a Claude Code notification.
# Switches to the correct tmux session:window.pane and brings terminal to front.
#
# Arguments:
#   $1 - tmux_location in format "session:window.pane" (e.g., "main:2.1")

set -e

LOCATION="$1"

if [[ -z "$LOCATION" ]]; then
    echo "Error: No tmux location provided" >&2
    exit 1
fi

# Find tmux binary
TMUX=$(whence -p tmux 2>/dev/null || echo "/opt/homebrew/bin/tmux")

if [[ ! -x "$TMUX" ]]; then
    echo "Error: tmux not found" >&2
    exit 1
fi

# Parse location: session:window.pane
# Examples: "main:2.1", "dev:0", "work:3.0"
SESSION="${LOCATION%%:*}"
WINDOW_PANE="${LOCATION#*:}"
WINDOW="${WINDOW_PANE%%.*}"
PANE="${WINDOW_PANE#*.}"

# If no pane specified (window_pane equals window), default to pane 0
if [[ "$PANE" == "$WINDOW" ]]; then
    PANE=""
fi

# Check if session exists
if ! "$TMUX" has-session -t "$SESSION" 2>/dev/null; then
    echo "Error: tmux session '$SESSION' not found" >&2
    exit 1
fi

# Switch to the session and window
"$TMUX" switch-client -t "$SESSION" 2>/dev/null || true
"$TMUX" select-window -t "$SESSION:$WINDOW" 2>/dev/null || true

# Select pane if specified
if [[ -n "$PANE" ]]; then
    "$TMUX" select-pane -t "$SESSION:$WINDOW.$PANE" 2>/dev/null || true
fi

# Bring iTerm2 to front
osascript -e 'tell application "iTerm2" to activate'

# Log for debugging (optional)
# echo "$(date '+%Y-%m-%d %H:%M:%S') - Navigated to $LOCATION" >> /tmp/claude-notifications.log
