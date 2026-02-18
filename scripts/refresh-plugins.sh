#!/bin/bash

# Product Forge Plugin Cache Refresh Script
# Validates plugin cache state and refreshes outdated/corrupted plugins
#
# Usage: ./scripts/refresh-plugins.sh [--dry-run] [--force] [--status] [plugin-name]
# Examples:
#   ./scripts/refresh-plugins.sh              # Check and refresh if needed
#   ./scripts/refresh-plugins.sh --status     # Show cache status only
#   ./scripts/refresh-plugins.sh --dry-run    # Preview changes
#   ./scripts/refresh-plugins.sh --force      # Force refresh all plugins
#   ./scripts/refresh-plugins.sh product-design  # Refresh specific plugin

set -e

# === CONFIGURATION ===

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"
CACHE_DIR="$HOME/.claude/plugins/cache/product-forge-marketplace"
INSTALLED_FILE="$HOME/.claude/plugins/installed_plugins_v2.json"
MARKETPLACE_FILE="$HOME/.claude/plugins/known_marketplaces.json"

# === GLOBAL STATE ===

DRY_RUN=false
FORCE=false
STATUS_ONLY=false
TARGET_PLUGIN=""

SOURCE_SHA=""
TOTAL_PLUGINS=0
OK_PLUGINS=0
OUTDATED_PLUGINS=0
CORRUPTED_PLUGINS=0
INVALID_PLUGINS=0
MISSING_PLUGINS=0

# Store status and issues in a more compatible format
# Format: "plugin_name|status|issue"
PLUGIN_DATA=""

# === UTILITY FUNCTIONS ===

function log_info() {
    echo "ℹ️  $1"
}

function log_success() {
    echo "✅ $1"
}

function log_warn() {
    echo "⚠️  $1"
}

function log_error() {
    echo "❌ $1"
}

function log_section() {
    echo ""
    echo "========================================================"
    echo "$1"
    echo "========================================================"
    echo ""
}

# === ARGUMENT PARSING ===

function parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --status)
                STATUS_ONLY=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                exit 1
                ;;
            *)
                TARGET_PLUGIN="$1"
                shift
                ;;
        esac
    done
}

# === PREREQUISITE CHECKS ===

function check_prerequisites() {
    if ! command -v claude &> /dev/null; then
        log_error "'claude' command not found"
        echo "Please install Claude Code: https://docs.claude.com/claude-code"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        log_error "'git' command not found"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "'jq' command not found"
        echo "Install: brew install jq (macOS) or apt-get install jq (Linux)"
        exit 1
    fi

    if [ ! -d "$REPO_ROOT/.git" ]; then
        log_error "Not a git repository: $REPO_ROOT"
        exit 1
    fi

    log_success "Prerequisites met: claude, git, jq available"
}

# === GIT OPERATIONS ===

function get_source_sha() {
    git -C "$REPO_ROOT" rev-parse HEAD
}

function check_git_state() {
    if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
        log_warn "Source repository has uncommitted changes"
        echo "Git SHA may not reflect actual plugin state"
        echo ""
        if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ] && [ "$STATUS_ONLY" = false ]; then
            read -p "Continue anyway? (y/N) " -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                exit 0
            fi
        fi
        echo ""
    fi
}

# === JSON OPERATIONS ===

function get_installed_sha() {
    local plugin_name="$1"
    jq -r ".plugins[\"${plugin_name}@product-forge-marketplace\"][0].gitCommitSha // \"\"" "$INSTALLED_FILE" 2>/dev/null || echo ""
}

function check_marketplace_registered() {
    if [ ! -f "$MARKETPLACE_FILE" ]; then
        return 1
    fi
    jq -e 'has("product-forge-marketplace")' "$MARKETPLACE_FILE" &>/dev/null
}

# === VALIDATION & DETECTION ===

function validate_plugin_cache() {
    local plugin_name="$1"
    local cache_path="$CACHE_DIR/$plugin_name/1.0.0"

    [ -d "$cache_path" ]
}

function validate_plugin_structure() {
    local plugin_dir="$1"
    (unset CLAUDECODE; claude plugin validate "$plugin_dir" &>/dev/null)
}

function detect_issues() {
    SOURCE_SHA=$(get_source_sha)

    # Check if installed_plugins_v2.json exists
    if [ ! -f "$INSTALLED_FILE" ]; then
        log_warn "No installed plugins file found"
        echo "This suggests plugins were never installed"
        echo ""
    fi

    # Iterate through all plugins in source
    for plugin_dir in "$PLUGINS_DIR"/*; do
        if [ ! -d "$plugin_dir" ]; then
            continue
        fi

        local plugin_name=$(basename "$plugin_dir")
        local status="UNKNOWN"
        local issue="Unknown issue"

        TOTAL_PLUGINS=$((TOTAL_PLUGINS + 1))

        # Check if plugin is installed
        if [ ! -f "$INSTALLED_FILE" ]; then
            status="MISSING"
            issue="Not installed (no installed_plugins_v2.json)"
            MISSING_PLUGINS=$((MISSING_PLUGINS + 1))
        else
            local installed_sha=$(get_installed_sha "$plugin_name")

            if [ -z "$installed_sha" ]; then
                status="MISSING"
                issue="Not in installed_plugins_v2.json"
                MISSING_PLUGINS=$((MISSING_PLUGINS + 1))
            elif [ "$installed_sha" != "$SOURCE_SHA" ]; then
                status="OUTDATED"
                issue="SHA mismatch (installed: ${installed_sha:0:7}, source: ${SOURCE_SHA:0:7})"
                OUTDATED_PLUGINS=$((OUTDATED_PLUGINS + 1))
            elif ! validate_plugin_cache "$plugin_name"; then
                status="CORRUPTED"
                issue="Cache directory missing"
                CORRUPTED_PLUGINS=$((CORRUPTED_PLUGINS + 1))
            elif ! validate_plugin_structure "$plugin_dir"; then
                status="INVALID"
                issue="Failed validation (claude plugin validate)"
                INVALID_PLUGINS=$((INVALID_PLUGINS + 1))
            else
                status="OK"
                issue="All checks passed"
                OK_PLUGINS=$((OK_PLUGINS + 1))
            fi
        fi

        # Store data in format: "plugin_name|status|issue"
        PLUGIN_DATA="$PLUGIN_DATA
$plugin_name|$status|$issue"
    done
}

# === REPORTING ===

function generate_report() {
    log_section "Plugin Cache Status Report"

    echo "Source Repository: $REPO_ROOT"
    echo "Source SHA: ${SOURCE_SHA:0:7}"
    echo "Cache Directory: $CACHE_DIR"
    echo ""

    echo "Summary:"
    echo "  Total plugins: $TOTAL_PLUGINS"
    echo "  OK: $OK_PLUGINS"
    echo "  Outdated: $OUTDATED_PLUGINS"
    echo "  Corrupted: $CORRUPTED_PLUGINS"
    echo "  Invalid: $INVALID_PLUGINS"
    echo "  Missing: $MISSING_PLUGINS"
    echo ""

    echo "Plugin Status:"
    echo "----------------------------------------"

    # Process plugin data sorted
    echo "$PLUGIN_DATA" | tail -n +2 | sort | while IFS='|' read -r plugin_name status issue; do
        case "$status" in
            "OK")
                log_success "$plugin_name"
                ;;
            "OUTDATED")
                log_warn "$plugin_name"
                if [ "$VERBOSE" = true ]; then
                    echo "        Issue: $issue"
                fi
                ;;
            "CORRUPTED")
                log_error "$plugin_name"
                if [ "$VERBOSE" = true ]; then
                    echo "        Issue: $issue"
                fi
                ;;
            "INVALID")
                log_error "$plugin_name"
                if [ "$VERBOSE" = true ]; then
                    echo "        Issue: $issue"
                fi
                ;;
            "MISSING")
                echo "⭕ $plugin_name"
                if [ "$VERBOSE" = true ]; then
                    echo "        Issue: $issue"
                fi
                ;;
        esac
    done

    echo ""
}

function needs_refresh() {
    [ $OUTDATED_PLUGINS -gt 0 ] || [ $CORRUPTED_PLUGINS -gt 0 ] || [ $INVALID_PLUGINS -gt 0 ] || [ $MISSING_PLUGINS -gt 0 ]
}

# === CLEANUP & INSTALLATION ===

function backup_state() {
    if [ -f "$INSTALLED_FILE" ]; then
        local backup_file="${INSTALLED_FILE}.backup-$(date +%Y%m%d-%H%M%S)"
        if [ "$DRY_RUN" = false ]; then
            cp "$INSTALLED_FILE" "$backup_file"
            log_success "Backed up installed_plugins_v2.json to $backup_file"
        else
            echo "[DRY RUN] Would backup to: $backup_file"
        fi
    fi
}

function clear_cache_for_plugin() {
    local plugin_name="$1"
    local cache_path="$CACHE_DIR/$plugin_name"

    if [ -d "$cache_path" ]; then
        if [ "$DRY_RUN" = false ]; then
            rm -rf "$cache_path"
            log_success "Cleared cache: $plugin_name"
        else
            echo "[DRY RUN] Would clear: $cache_path"
        fi
    else
        log_warn "Cache already missing: $plugin_name"
    fi
}

function ensure_marketplace_registered() {
    if check_marketplace_registered; then
        return 0
    fi

    log_warn "Marketplace not registered, re-adding..."

    if [ "$DRY_RUN" = false ]; then
        if (unset CLAUDECODE; claude plugin marketplace add "$REPO_ROOT"); then
            log_success "Marketplace re-added"
            return 0
        else
            log_error "Failed to re-add marketplace"
            echo "Try manually: claude plugin marketplace add $REPO_ROOT"
            return 1
        fi
    else
        echo "[DRY RUN] Would run: claude plugin marketplace add $REPO_ROOT"
        return 0
    fi
}

function reinstall_plugin() {
    local plugin_name="$1"

    if [ "$DRY_RUN" = false ]; then
        if (unset CLAUDECODE; claude plugin install "${plugin_name}@product-forge-marketplace"); then
            log_success "Installed: $plugin_name"
            return 0
        else
            log_error "Failed to install: $plugin_name"
            return 1
        fi
    else
        echo "[DRY RUN] Would run: claude plugin install ${plugin_name}@product-forge-marketplace"
        return 0
    fi
}

function verify_installation() {
    local plugin_name="$1"
    local plugin_dir="$PLUGINS_DIR/$plugin_name"

    if [ "$DRY_RUN" = true ]; then
        return 0
    fi

    # Check SHA
    local new_installed_sha=$(get_installed_sha "$plugin_name")
    if [ "$new_installed_sha" = "$SOURCE_SHA" ]; then
        log_success "SHA verified: $plugin_name (${new_installed_sha:0:7})"
    else
        log_warn "SHA mismatch after install: $plugin_name (expected: ${SOURCE_SHA:0:7}, got: ${new_installed_sha:0:7})"
    fi

    # Check validation
    if validate_plugin_structure "$plugin_dir"; then
        log_success "Validation passed: $plugin_name"
    else
        log_error "Validation failed: $plugin_name"
    fi
}

# === MAIN FLOW ===

function main() {
    parse_arguments "$@"

    # Show current mode
    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN MODE - No changes will be made"
        echo ""
    fi

    if [ "$STATUS_ONLY" = true ]; then
        log_info "Status check mode - will not make changes"
        echo ""
    fi

    # Phase 1: Prerequisites
    log_section "Phase 1: Checking Prerequisites"
    check_prerequisites
    check_git_state

    # Phase 2: Detection
    log_section "Phase 2: Detecting Issues"
    detect_issues

    # Phase 3: Reporting
    generate_report

    # Early exit for status-only mode
    if [ "$STATUS_ONLY" = true ]; then
        exit 0
    fi

    # Check if refresh is needed
    if ! needs_refresh && [ "$FORCE" = false ]; then
        log_section "Result"
        log_success "All plugins are up to date and valid!"
        echo ""
        exit 0
    fi

    # Ask for confirmation (unless --force or --dry-run)
    if [ "$DRY_RUN" = false ] && [ "$FORCE" = false ]; then
        echo ""
        read -p "Proceed with refresh? (y/N) " -r response
        echo ""
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi
    fi

    # Phase 4: Cleanup
    log_section "Phase 4: Backing Up and Clearing Cache"
    backup_state

    # Determine which plugins to refresh
    local plugins_to_refresh=""

    if [ -n "$TARGET_PLUGIN" ]; then
        plugins_to_refresh="$TARGET_PLUGIN"
    else
        # Refresh all problematic plugins, or all if forced
        echo "$PLUGIN_DATA" | tail -n +2 | while IFS='|' read -r plugin_name status _; do
            if [ "$status" != "OK" ] || [ "$FORCE" = true ]; then
                echo "$plugin_name"
            fi
        done > /tmp/plugins_to_refresh.tmp
        plugins_to_refresh=$(cat /tmp/plugins_to_refresh.tmp | tr '\n' ' ')
        rm -f /tmp/plugins_to_refresh.tmp
    fi

    # Clear cache for plugins being refreshed
    for plugin_name in $plugins_to_refresh; do
        clear_cache_for_plugin "$plugin_name"
    done

    # Phase 5: Reinstallation
    log_section "Phase 5: Reinstalling Plugins"

    # Ensure marketplace is registered
    if ! ensure_marketplace_registered; then
        exit 1
    fi

    echo ""

    # Reinstall each plugin
    local successful_reinstalls=0
    local failed_reinstalls=0

    for plugin_name in $plugins_to_refresh; do
        if [ -n "$plugin_name" ]; then
            if reinstall_plugin "$plugin_name"; then
                successful_reinstalls=$((successful_reinstalls + 1))
            else
                failed_reinstalls=$((failed_reinstalls + 1))
            fi
        fi
    done

    # Phase 6: Verification
    log_section "Phase 6: Verifying Installations"

    if [ "$DRY_RUN" = false ]; then
        for plugin_name in $plugins_to_refresh; do
            if [ -n "$plugin_name" ]; then
                verify_installation "$plugin_name"
            fi
        done
    fi

    # Final Report
    log_section "Refresh Complete"

    local plugin_count=$(echo "$plugins_to_refresh" | wc -w)
    echo "Results:"
    echo "  Plugins processed: $plugin_count"
    echo "  Successful: $successful_reinstalls"
    echo "  Failed: $failed_reinstalls"
    echo ""

    if [ $failed_reinstalls -gt 0 ]; then
        log_error "Some plugins failed to reinstall"
        echo ""
        echo "Troubleshooting steps:"
        echo "  1. Check that source repository is up to date: git pull"
        echo "  2. Check that plugins are valid: ./scripts/validate-all-plugins.sh"
        echo "  3. Try manually: claude plugin install <plugin>@product-forge-marketplace"
        echo "  4. Check Claude Code logs for detailed error information"
        echo ""
        exit 1
    else
        log_success "All plugins refreshed successfully!"
        echo ""
        echo "Source SHA: ${SOURCE_SHA:0:7}"
        echo "All installed plugins now match source"
        echo ""
        exit 0
    fi
}

# === ENTRY POINT ===

main "$@"
