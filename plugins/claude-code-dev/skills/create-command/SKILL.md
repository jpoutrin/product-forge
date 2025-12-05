---
name: create-command
description: Create a new Claude Code slash command with proper YAML frontmatter structure. Use when the user wants to add a custom slash command to a plugin. Handles command file creation with description and argument hints.
---

# Create Command Skill

Create new Claude Code slash commands with proper configuration.

## Command File Format

Commands are markdown files in the `commands/` directory with YAML frontmatter:

```markdown
---
description: Short description shown in /help
argument-hint: <required-arg> [optional-arg]
---

# Command Name

Instructions for Claude when this command is invoked...
```

## Required Frontmatter Fields

| Field | Description | Example |
|-------|-------------|---------|
| `description` | One-line summary shown in `/help` | `Create a new feature branch` |
| `argument-hint` | Arguments shown after command name | `<branch-name> [--from <base>]` |

## Argument Hint Conventions

- `<name>` - Required argument
- `[name]` - Optional argument
- `[--flag]` - Optional flag
- `[--option <value>]` - Optional flag with value
- `""` - No arguments (empty string)

## Examples

### Command with Required Argument
```markdown
---
description: Create a new feature branch
argument-hint: <branch-name>
---
```

### Command with Multiple Arguments
```markdown
---
description: Deploy to specified environment
argument-hint: <environment> [--dry-run] [--force]
---
```

### Command with No Arguments
```markdown
---
description: Show project status overview
argument-hint: ""
---
```

### Command with Optional Arguments Only
```markdown
---
description: List all tasks with optional filtering
argument-hint: "[--status <status>] [--format <format>]"
---
```

## Command Body Best Practices

1. **Be specific**: Tell Claude exactly what to do
2. **Include context**: Reference relevant files or patterns
3. **Define output format**: Specify how results should be presented
4. **Handle edge cases**: Include instructions for common issues

## Example Command

```markdown
---
description: Generate a changelog from recent commits
argument-hint: "[--since <date>] [--format <format>]"
---

# Generate Changelog

Generate a changelog from git commits.

## Process

1. Get commits since the specified date (default: last tag)
2. Group commits by type (feat, fix, docs, etc.)
3. Format as markdown changelog

## Output Format

```markdown
## [Version] - YYYY-MM-DD

### Added
- Feature descriptions

### Fixed
- Bug fix descriptions

### Changed
- Change descriptions
```

## Arguments

- `--since`: Start date or tag (default: last tag)
- `--format`: Output format: `markdown`, `json`, `plain`
```

## File Location

Save command files to:
```
plugins/<plugin-name>/commands/<command-name>.md
```

The command name becomes the slash command: `/command-name`
