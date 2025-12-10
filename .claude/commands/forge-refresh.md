---
description: Validate and refresh Product Forge plugin cache
argument-hint: "[--dry-run] [--force] [--status] [--verbose] [plugin-name]"
keywords: cache, refresh, validate, reinstall, update, maintenance
---

# forge-refresh

**Category**: Plugin Management

## Usage

```bash
/forge-refresh [options] [plugin-name]
```

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview actions without making changes |
| `--force` | Force reinstall even if all plugins are up to date |
| `--status` | Show current cache status only (no changes made) |
| `--verbose` | Show detailed issue descriptions for each plugin |
| `[plugin-name]` | Optional: Refresh only specific plugin (e.g., `product-design`) |

## Purpose

Validates Product Forge plugin cache state and refreshes outdated, corrupted, or invalid plugins. Use this command when:

- Claude Code becomes unstable or unresponsive
- Plugins don't appear or respond in Claude Code
- Skills, commands, or agents are not recognized
- After pulling updates to the source repository
- When cache appears to be out of sync with source

## How It Works

This command performs six phases of cache management:

1. **Prerequisites** - Verifies claude CLI, git, and jq are available
2. **Detection** - Scans plugin cache and compares with source repository
3. **Reporting** - Shows status of each plugin and any issues found
4. **Backup** - Creates timestamped backup of current installation state
5. **Reinstallation** - Clears stale cache and reinstalls plugins
6. **Verification** - Confirms installations succeeded and match source

## What Gets Checked

For each plugin, the command validates:

- **SHA Match**: Installed version matches source repository commit
- **Cache Exists**: Plugin cache directory is present
- **Plugin Valid**: Plugin structure passes validation checks

Status indicators:
- ✅ **OK** - Plugin is up to date and valid
- ⚠️ **OUTDATED** - Source has newer commits
- ❌ **CORRUPTED** - Cache directory missing
- ❌ **INVALID** - Plugin structure validation failed
- ⭕ **MISSING** - Plugin not installed at all

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Parse the Arguments

Extract flags and plugin name from the command arguments:
- `--dry-run`, `--force`, `--status`, `--verbose` are boolean flags
- The last argument (if not a flag) is the optional plugin name

### 2. Delegate to Script

Run the refresh script with all provided arguments:

```bash
./scripts/refresh-plugins.sh "$@"
```

### 3. Interpret the Output

The script will display:
- Status report with emoji indicators for each plugin
- List of issues detected (if any)
- Prompts for confirmation (unless `--force` or `--dry-run`)
- Progress during installation
- Final summary with results

### 4. Exit Codes

The script exits with:
- `0` - Success (all plugins refreshed successfully)
- `1` - Failure (some plugins failed to install, or prerequisites missing)
- `2` - (reserved for future use)

### 5. Display Results

Display all output from the script to the user. If there are failures:

1. Suggest checking the troubleshooting section in the output
2. Offer to run individual diagnostics like `./scripts/validate-all-plugins.sh`
3. Recommend checking Claude Code logs if the issue persists

## Examples

### Check current cache status

```bash
/forge-refresh --status
```

Output shows status of all plugins without making any changes.

### Preview what would be refreshed

```bash
/forge-refresh --dry-run
```

Shows exactly what actions would be taken, but makes no changes.

### Refresh with detailed output

```bash
/forge-refresh --verbose
```

Shows status of all plugins with detailed issue descriptions.

### Force refresh all plugins

```bash
/forge-refresh --force
```

Reinstalls all plugins regardless of current status. Use when you want a clean slate.

### Refresh specific plugin only

```bash
/forge-refresh product-design
```

Only clears and reinstalls the `product-design` plugin, leaving others untouched.

### Combine options

```bash
/forge-refresh --dry-run --verbose
```

Preview with detailed issue descriptions, no changes made.

## Common Scenarios

### Scenario 1: After pulling source updates

```bash
git pull
/forge-refresh
```

Refresh plugins after pulling new commits to match the updated source.

### Scenario 2: Plugins not appearing in Claude

```bash
/forge-refresh --force
```

Force a complete reinstall if plugins became invisible or unresponsive.

### Scenario 3: Check without making changes

```bash
/forge-refresh --dry-run
```

Preview what would be done before proceeding with actual refresh.

### Scenario 4: Diagnose single plugin issue

```bash
/forge-refresh --verbose product-design
```

Check the status of a specific plugin with detailed diagnostic information.

## Troubleshooting

### If the command fails

The script will suggest troubleshooting steps in its output. Common next steps:

1. **Verify plugins are valid:**
   ```bash
   ./scripts/validate-all-plugins.sh
   ```

2. **Check if source repo is up to date:**
   ```bash
   git pull
   /forge-refresh
   ```

3. **Try single plugin install:**
   ```bash
   claude plugin install product-design@product-forge-marketplace
   ```

4. **Check Claude Code logs:**
   Look in your Claude Code settings for detailed error logs if the above steps don't resolve the issue.

### If marketplace is not registered

The script will automatically attempt to re-add the marketplace during reinstallation. If this fails, you can manually add it:

```bash
claude plugin marketplace add /Users/jeremiepoutrin/projects/github/jpoutrin/product-forge
```

### If plugins still don't work after refresh

- Restart Claude Code
- Close all Claude Code windows and reopen
- Check your internet connection
- Review Claude Code logs for system errors

## Related Commands

| Command | Purpose |
|---------|---------|
| `/forge-help` | List all available Product Forge agents, skills, and commands |

## Related Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/validate-all-plugins.sh` | Validate all plugins or a specific plugin |
| `./scripts/validate-marketplace.py` | Validate marketplace.json schema |
| `./scripts/generate-forge-index.py` | Regenerate command/skill/agent index |
