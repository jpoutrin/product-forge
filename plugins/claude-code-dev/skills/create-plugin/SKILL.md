---
name: create-plugin
description: Create a new Claude Code plugin with proper directory structure and manifest. Use when the user wants to create a new plugin from scratch. Sets up plugin.json, directory structure, and optional components.
---

# Create Plugin Skill

Create new Claude Code plugins with proper structure and configuration.

## Plugin Directory Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (required)
├── agents/                   # Agent definitions (optional)
│   └── agent-name.md
├── commands/                 # Slash commands (optional)
│   └── command-name.md
├── skills/                   # Agent skills (optional)
│   └── skill-name/
│       └── SKILL.md
└── hooks/                    # Event handlers (optional)
    └── hooks.json
```

## Plugin Manifest (plugin.json)

### Minimal Required Manifest

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": {
    "name": "Your Name",
    "email": "your@email.com"
  }
}
```

### Full Manifest with Components

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": {
    "name": "Your Name",
    "email": "your@email.com"
  },
  "commands": {
    "command-name": {
      "description": "What this command does",
      "source": "../commands/command-name.md"
    }
  },
  "agents": "./agents/",
  "skills": "./skills/"
}
```

## CRITICAL: Manifest Format Rules

### Commands Configuration

Commands MUST use `"source"` (NOT `"file"`):

**CORRECT:**
```json
"commands": {
  "my-command": {
    "description": "Command description",
    "source": "../commands/my-command.md"
  }
}
```

**WRONG - Will cause validation errors:**
```json
"commands": {
  "my-command": {
    "description": "Command description",
    "file": "../commands/my-command.md",     // WRONG: use "source"
    "arguments": "<arg>"                      // WRONG: use frontmatter
  }
}
```

### Agents and Skills Configuration

Agents and skills MUST use directory paths (NOT object format):

**CORRECT:**
```json
{
  "agents": "./agents/",
  "skills": "./skills/"
}
```

**WRONG - Will cause validation errors:**
```json
{
  "agents": {
    "agent-name": {
      "description": "...",
      "file": "../agents/agent-name.md"
    }
  },
  "skills": {
    "skill-name": {
      "description": "...",
      "file": "../skills/skill-name.md",
      "triggers": ["keyword"]
    }
  }
}
```

### Command Arguments

Command arguments go in the markdown file's frontmatter, NOT in plugin.json:

```markdown
---
description: My command description
argument-hint: <required-arg> [--optional-flag]
---
```

## Manifest Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Plugin identifier (kebab-case) |
| `version` | Yes | Semantic version (e.g., "1.0.0") |
| `description` | Yes | Brief description of plugin purpose |
| `author.name` | Yes | Author name |
| `author.email` | No | Author email |
| `commands` | No | Object with command definitions |
| `agents` | No | Directory path string: `"./agents/"` |
| `skills` | No | Directory path string: `"./skills/"` |

## Creation Process

1. **Plan the plugin**
   - Define the plugin's purpose
   - List components needed (commands, agents, skills)
   - Choose a descriptive name

2. **Create directory structure**
   ```bash
   mkdir -p plugin-name/.claude-plugin
   mkdir -p plugin-name/agents
   mkdir -p plugin-name/commands
   mkdir -p plugin-name/skills
   ```

3. **Create plugin.json**
   ```json
   {
     "name": "plugin-name",
     "version": "1.0.0",
     "description": "Plugin description",
     "author": {
       "name": "Author Name"
     },
     "commands": {
       "my-command": {
         "description": "Command description",
         "source": "../commands/my-command.md"
       }
     },
     "agents": "./agents/",
     "skills": "./skills/"
   }
   ```

4. **Add components**
   - Add agents to `agents/` with proper frontmatter
   - Add commands to `commands/` with proper frontmatter
   - Add skills to `skills/skill-name/SKILL.md`

5. **Add to marketplace**
   Update marketplace.json to include the new plugin

## Example Plugin

### plugin.json
```json
{
  "name": "code-quality",
  "version": "1.0.0",
  "description": "Code quality tools including linting, formatting, and review",
  "author": {
    "name": "Developer",
    "email": "dev@example.com"
  },
  "commands": {
    "lint": {
      "description": "Run linter on codebase",
      "source": "../commands/lint.md"
    },
    "format": {
      "description": "Format code files",
      "source": "../commands/format.md"
    }
  },
  "agents": "./agents/",
  "skills": "./skills/"
}
```

### Directory Structure
```
code-quality/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── code-reviewer.md
├── commands/
│   ├── lint.md
│   └── format.md
└── skills/
    └── code-standards/
        └── SKILL.md
```

## Adding to Marketplace

Update the marketplace.json to include your plugin:

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "description": "Plugin description",
      "category": "development"
    }
  ]
}
```

## Testing Your Plugin

1. Add marketplace: `/plugin marketplace add ./path-to-marketplace`
2. Install plugin: `/plugin install plugin-name@marketplace-name`
3. Verify with `/help` to see commands
4. Test components individually

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Command must have either "source" or "content"` | Using `"file"` instead of `"source"` | Change to `"source": "../path.md"` |
| `agents: Invalid input` | Using object format for agents | Change to `"agents": "./agents/"` |
| `skills: Invalid input` | Using object format for skills | Change to `"skills": "./skills/"` |
