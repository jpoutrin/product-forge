# Claude Code Development Plugin

Tools for creating and managing Claude Code plugins, agents, commands, skills, and feedback loops.

## Skills

### create-skill
**Create Claude Code agent skills**

Create new Claude Code agent skills that Claude invokes autonomously based on task context. Handles skill folder creation with SKILL.md and optional reference files.

**When to use**: User wants to create a skill, add a model-invoked skill, or asks how to define skills

### create-command
**Create Claude Code commands**

Create new Claude Code user-invoked commands with proper markdown format and execution instructions.

**When to use**: User wants to create a command, add a slash command, or asks how to define commands

### create-agent
**Create Claude Code agents**

Create new Claude Code specialized agents with proper markdown format, tool configuration, and model selection.

**When to use**: User wants to create an agent, add a specialized agent, or asks how to define agents

### create-plugin
**Create Claude Code plugins**

Create new Claude Code plugins with proper structure, manifest, and component organization.

**When to use**: User wants to create a plugin, start a new plugin project, or asks how to structure plugins

### mcp-setup
**MCP server setup guidance**

Guide for installing and configuring MCP servers in Claude Code.

**When to use**: User wants to add an MCP server, configure MCP, or asks about MCP setup

### pattern-detection
**Recognize reusable patterns for Product Forge**

Identify reusable patterns, best practices, and workflow automations during implementation that could become Product Forge skills, commands, or templates.

**When to use**: Claude implements similar patterns multiple times, creates reusable structures, or applies best practices that could benefit others

**Covers**:
- Code patterns (factories, services, error handling, API patterns)
- Workflow patterns (setup, review, deployment, documentation)
- Configuration patterns (tools, environments, integrations)
- Pattern quality criteria and examples

## Commands

### /install-playwright-mcp
Install Playwright MCP server for browser automation in Claude Code. Supports scope selection and headless mode.

### /enable-feedback-hooks
Enable feedback capture hooks for the current project. Opts-in to AI-powered analysis at session end for Product Forge improvements.

**Usage**:
```bash
/enable-feedback-hooks          # Enable for current project
/enable-feedback-hooks --disable  # Disable for current project
```

### /sync-feedback
Review and sync captured feedback to Product Forge. Provides statistics, interactive review, and export to GitHub issues.

**Usage**:
```bash
/sync-feedback              # Interactive review
/sync-feedback --status     # Show statistics
/sync-feedback --review     # Review pending items
/sync-feedback --export     # Export to GitHub issues
```

## Feedback System

The plugin includes a feedback capture system that:
1. **Captures** improvements, skill ideas, command ideas, bug reports, and patterns
2. **Stores** feedback locally in `~/.claude/learnings/`
3. **Reviews** via `/sync-feedback` command
4. **Submits** to Product Forge for consideration

### Setup

```bash
# Enable in your project
/enable-feedback-hooks

# Review captured feedback
/sync-feedback --status
/sync-feedback --review
```

### How It Works

```
Session ends → Haiku analyzes → Saves to ~/.claude/learnings/
                                         ↓
                            Use /sync-feedback to review
```

All feedback stays local until you explicitly submit it.
