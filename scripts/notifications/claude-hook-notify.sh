#!/bin/bash
# Claude hook notification wrapper with logging
# Usage: claude-hook-notify.sh <event_name>

EVENT_NAME="${1:-Unknown}"
LOG_FILE="$HOME/Library/Logs/claude-hooks/claude-hooks.log"

# Get tmux location dynamically (not from static env vars)
if [ -n "$TMUX" ]; then
  TMUX_LOCATION=$(tmux display-message -p '#{session_name}:#{window_index}.#{pane_index}' 2>/dev/null)
  TMUX_SESSION=$(tmux display-message -p '#{session_name}' 2>/dev/null)
  TMUX_WINDOW=$(tmux display-message -p '#{window_name}' 2>/dev/null)
else
  TMUX_LOCATION="${WS_TMUX_LOCATION:-unknown}"
  TMUX_SESSION="${WS_TMUX_SESSION_NAME:-unknown}"
  TMUX_WINDOW="${WS_TMUX_WINDOW_NAME:-unknown}"
fi

# Build payload
PAYLOAD=$(jq -n \
  --arg tmux_location "$TMUX_LOCATION" \
  --arg tmux_session_name "$TMUX_SESSION" \
  --arg tmux_window_name "$TMUX_WINDOW" \
  --arg project "$(basename "$PWD")" \
  --arg cwd "$PWD" \
  --arg hook_event_name "$EVENT_NAME" \
  --arg session_id "$CLAUDE_SESSION_ID" \
  '{tmux_location: $tmux_location, tmux_session_name: $tmux_session_name, tmux_window_name: $tmux_window_name, project: $project, cwd: $cwd, hook_event_name: $hook_event_name, session_id: $session_id}')

# Log to file
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $PAYLOAD" >> "$LOG_FILE"

# Send to webhook
echo "$PAYLOAD" | curl -s -X POST -H 'Content-Type: application/json' -d @- http://localhost:9000/hooks/claude-notify
