#!/bin/bash

# Product Forge Learnings Directory Initialization
# Creates the ~/.claude/learnings/ directory structure for feedback storage
#
# Usage: ./scripts/hooks/init-learnings.sh [--force]

set -e

LEARNINGS_DIR="$HOME/.claude/learnings"

# === UTILITY FUNCTIONS ===

function log_info() {
    echo "ℹ️  $1"
}

function log_success() {
    echo "✅ $1"
}

function log_error() {
    echo "❌ $1" >&2
}

# === MAIN ===

function init_learnings() {
    local force="${1:-false}"

    # Check if already initialized
    if [[ -d "$LEARNINGS_DIR" && "$force" != "--force" ]]; then
        log_info "Learnings directory already exists at $LEARNINGS_DIR"
        log_info "Use --force to reinitialize"
        return 0
    fi

    log_info "Initializing learnings directory at $LEARNINGS_DIR"

    # Create directory structure
    mkdir -p "$LEARNINGS_DIR/projects"
    mkdir -p "$LEARNINGS_DIR/cross-project"
    mkdir -p "$LEARNINGS_DIR/synced"

    # Create projects.json if it doesn't exist
    if [[ ! -f "$LEARNINGS_DIR/projects.json" ]]; then
        cat > "$LEARNINGS_DIR/projects.json" << 'EOF'
{
  "version": "1.0",
  "projects": {}
}
EOF
        log_success "Created projects.json"
    fi

    # Create stats.json if it doesn't exist
    if [[ ! -f "$LEARNINGS_DIR/stats.json" ]]; then
        cat > "$LEARNINGS_DIR/stats.json" << 'EOF'
{
  "version": "1.0",
  "total_feedback": 0,
  "by_type": {
    "improvement": 0,
    "skill-idea": 0,
    "command-idea": 0,
    "bug-report": 0,
    "pattern": 0
  },
  "by_project": {},
  "last_updated": null
}
EOF
        log_success "Created stats.json"
    fi

    log_success "Learnings directory initialized at $LEARNINGS_DIR"

    # Show structure
    echo ""
    echo "Directory structure:"
    echo "  $LEARNINGS_DIR/"
    echo "  ├── projects.json       # Registry of opted-in projects"
    echo "  ├── stats.json          # Global feedback statistics"
    echo "  ├── projects/           # Per-project feedback"
    echo "  │   └── {project-slug}/"
    echo "  │       └── feedback/"
    echo "  │           ├── improvement/"
    echo "  │           ├── skill-idea/"
    echo "  │           ├── command-idea/"
    echo "  │           ├── bug-report/"
    echo "  │           └── pattern/"
    echo "  ├── cross-project/      # Cross-project patterns"
    echo "  └── synced/             # Archived after sync"
    echo ""
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_learnings "$1"
fi
