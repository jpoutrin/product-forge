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

Minimal required manifest:

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

## Manifest Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Plugin identifier (kebab-case) |
| `version` | Yes | Semantic version (e.g., "1.0.0") |
| `description` | Yes | Brief description of plugin purpose |
| `author.name` | Yes | Author name |
| `author.email` | No | Author email |

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
     }
   }
   ```

4. **Add components**
   - Add agents to `agents/`
   - Add commands to `commands/`
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
  }
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
