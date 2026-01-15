#!/bin/bash
# notify-claude.sh - macOS notification for Claude Code sessions
#
# Called by webhook service when Claude triggers Stop/Notification hooks.
# Generates a native macOS notification with click-to-navigate support.
#
# Arguments (passed from webhook):
#   $1 - tmux_location (session:window.pane)
#   $2 - tmux_session_name
#   $3 - tmux_window_name
#   $4 - project name
#   $5 - current working directory
#   $6 - transcript_path
#   $7 - hook_event_name (Stop, Notification)
#   $8 - session_id

TMUX_LOCATION="${1:-unknown}"
SESSION_NAME="${2:-unknown}"
WINDOW_NAME="${3:-unknown}"
PROJECT="${4:-unknown}"
CWD="${5:-unknown}"
TRANSCRIPT="${6:-}"
HOOK_EVENT="${7:-Notification}"
SESSION_ID="${8:-}"

# Optional sender app (set NOTIFICATION_SENDER to customize which app icon appears)
# If not set, notifications appear from terminal-notifier itself
SENDER="${NOTIFICATION_SENDER:-}"

# Determine notification message based on hook event
if [ "$HOOK_EVENT" = "Stop" ]; then
    STATUS="done"
    SOUND="Glass"
else
    STATUS="waiting"
    SOUND="default"
fi

# Extract just the project folder name from CWD if project is unknown
if [ "$PROJECT" = "unknown" ] || [ -z "$PROJECT" ]; then
    PROJECT=$(basename "$CWD")
fi

# Build sender argument only if SENDER is set
SENDER_ARG=""
if [ -n "$SENDER" ]; then
    SENDER_ARG="-sender $SENDER"
fi

# Generate the notification (run in background to avoid blocking)
terminal-notifier \
    -title "Claude Code - $SESSION_NAME" \
    -subtitle "Claude is $STATUS" \
    -message "Project: $PROJECT (window: $WINDOW_NAME)" \
    -execute "/usr/bin/curl -s -X POST 'http://localhost:9000/hooks/go-tmux?tmux_location=$TMUX_LOCATION'" \
    -sound "$SOUND" \
    -group "claude-$SESSION_ID" \
    $SENDER_ARG &

# Log for debugging (optional - comment out in production)
# echo "$(date '+%Y-%m-%d %H:%M:%S') - Notification sent: $HOOK_EVENT for $PROJECT in $SESSION_NAME:$WINDOW_NAME" >> /tmp/claude-notifications.log
