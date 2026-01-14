# Claude Code tmux notification environment variables
# Add this to your ~/.zshrc or ~/.bashrc
#
# These variables are read by Claude hooks to identify which tmux pane
# triggered the notification, enabling click-to-navigate functionality.

if [ -n "$TMUX" ] && [ -z "$WS_TMUX_LOCATION" ]; then
    export WS_TMUX_LOCATION=$(tmux display-message -p '#{session_name}:#{window_index}.#{pane_index}')
    export WS_TMUX_SESSION_NAME=$(tmux display-message -p '#{session_name}')
    export WS_TMUX_WINDOW_NAME=$(tmux display-message -p '#{window_name}')
fi
