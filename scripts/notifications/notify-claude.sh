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

# Get current active tmux session:window from most recent client
# Returns: "session:window" (e.g., "main:2") or empty string
get_active_tmux_session_window() {
    # Get most recently active tmux client's session:window
    # Format: "timestamp session:window" - we sort by timestamp and take the latest
    local result=$(tmux list-clients -F '#{client_activity} #{session_name}:#{window_index}' 2>/dev/null | sort -rn | head -1)

    # Extract just the session:window part (remove timestamp)
    echo "${result#* }"
}

# Extract session:window from full location (strip pane)
# "main:2.1" -> "main:2"
get_session_window() {
    local location="$1"
    # Remove .pane suffix if present
    echo "${location%.*}"
}

# Focus detection: iTerm2 + same tmux session:window
# Args: $1 - notification tmux location (e.g., "main:2.1")
# Returns: 0 (skip notification) or 1 (send notification)
should_skip_notification() {
    local notification_location="$1"

    # Level 1: Check if iTerm2 is frontmost application
    local frontmost_app=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true' 2>/dev/null)
    if [ "$frontmost_app" != "iTerm2" ]; then
        return 1  # Not iTerm2, send notification
    fi

    # Level 2: Get current active tmux session:window
    local current_session_window=$(get_active_tmux_session_window)
    if [ -z "$current_session_window" ]; then
        return 1  # Can't detect tmux, send notification
    fi

    # Level 3: Compare session:window (ignore pane)
    local notification_session_window=$(get_session_window "$notification_location")
    if [ "$current_session_window" = "$notification_session_window" ]; then
        return 0  # Same session:window, skip notification
    else
        return 1  # Different session:window, send notification
    fi
}

# Optional sender app (set NOTIFICATION_SENDER to customize which app icon appears)
# If not set, notifications appear from terminal-notifier itself
SENDER="${NOTIFICATION_SENDER:-}"

# Enhanced focus detection: iTerm2 + exact tmux location
if should_skip_notification "$TMUX_LOCATION"; then
    # Uncomment for debugging:
    # echo "$(date '+%Y-%m-%d %H:%M:%S') - Skipped: Already focused on $TMUX_LOCATION" >> /tmp/claude-notifications.log
    exit 0
fi

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

# URL-encode the tmux location for the click action
# This handles special characters like spaces and ampersands in session names
ENCODED_LOCATION=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TMUX_LOCATION', safe=''))")

# Generate the notification (run in background to avoid blocking)
terminal-notifier \
    -title "Claude Code - $SESSION_NAME" \
    -subtitle "Claude is $STATUS" \
    -message "Project: $PROJECT (window: $WINDOW_NAME)" \
    -execute "/usr/bin/curl -s -X POST 'http://localhost:9000/hooks/go-tmux?tmux_location=$ENCODED_LOCATION'" \
    -sound "$SOUND" \
    -group "claude-$SESSION_ID" \
    $SENDER_ARG &

# Log for debugging (optional - uncomment to enable)
# echo "$(date '+%Y-%m-%d %H:%M:%S') - Notification sent: $HOOK_EVENT for $PROJECT in $TMUX_LOCATION" >> /tmp/claude-notifications.log
