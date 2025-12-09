---
name: parallel-agents
short: Orchestrate parallel multi-agent development
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
when: User wants to parallelize development, run multiple agents simultaneously, decompose a PRD into independent tasks, scale work across concurrent workstreams, or coordinate multi-agent workflows
---

# Parallel Agent Development

Orchestrate massively parallel development by decomposing work into independent tasks that multiple Claude Code instances can execute simultaneously.

## CLI Tool: cpo (Claude Parallel Orchestrator)

The `cpo` CLI tool handles parallel agent execution with git worktree isolation.

### Installation

```bash
pip install claude-parallel-orchestrator
# or
pipx install claude-parallel-orchestrator
```

### cpo Commands

| Command | Description |
|---------|-------------|
| `cpo init <dir> -t <tech-spec> -n <name>` | Initialize parallel directory |
| `cpo validate <dir>` | Validate manifest and structure |
| `cpo run <dir>` | Execute parallel agents |
| `cpo status <dir>` | Check execution status |

## Workflow Overview

```
/parallel-setup       -> One-time: creates parallel/ directory
         |
/parallel-decompose   -> Per Tech Spec: creates TS-XXXX-slug/ with all artifacts
         |
/parallel-run         -> Delegates to `cpo run` for execution
         |
/parallel-integrate   -> Verify & generate integration report
```

## Directory Structure

Each decomposition creates an isolated artifact folder keyed by Tech Spec:

```
project/
  parallel/                           # Created by /parallel-setup (one-time)
    README.md
    .gitignore
    TS-XXXX-{slug}/                   # Created by /parallel-decompose
      manifest.json                   # Regeneration metadata
      context.md                      # Shared project context (token-efficient)
      architecture.md                 # System design from Tech Spec
      task-graph.md                   # Dependency visualization (Mermaid)
      contracts/
        types.py (or types.ts)        # Shared domain types
        api-schema.yaml               # OpenAPI specification
      tasks/
        task-001-users.md             # Compact YAML format
        task-002-products.md
        ...
      prompts/
        agent-prompts.md              # All launch commands
        task-*.txt                    # Individual agent prompts
      integration-report.md           # Post-execution report
  tech-specs/                         # Source Tech Specs
    approved/TS-XXXX-slug.md
  CLAUDE.md                           # Project conventions
```

## Related Skills

This skill is part of a family of parallel development skills:

| Skill | Purpose |
|-------|---------|
| **parallel-decompose** | PRD decomposition workflow, task generation, contracts |
| **parallel-prompt-generator** | Generate agent prompts from task specs |
| **parallel-execution** | Git worktrees, parallel execution patterns, scripts |
| **parallel-task-format** | Task spec YAML format, scope notation, agent selection |
| **agent-tools** | Tool permissions, CLI syntax for agent restrictions |

## Quick Start

### Phase 1: Setup (One-Time)

```bash
/parallel-setup --tech django
```

Creates `parallel/` directory structure.

### Phase 2: Decomposition

```bash
/parallel-decompose docs/prd.md --tech-spec tech-specs/approved/TS-0042-inventory.md
```

Creates `parallel/TS-0042-inventory-system/` with:
- manifest.json, context.md, architecture.md
- contracts/ (types.py, api-schema.yaml)
- tasks/ (compact YAML task specs)
- prompts/ (agent launch commands)

### Phase 3: Execution

```bash
# Using /parallel-run (delegates to cpo)
/parallel-run parallel/TS-0042-inventory-system/

# Or using cpo directly
cpo run parallel/TS-0042-inventory-system/
```

### Phase 4: Integration

```bash
/parallel-integrate --parallel-dir parallel/TS-0042-inventory-system
```

Checks contract compliance, boundary compliance, runs tests, generates report.

## manifest.json Format

```json
{
  "tech_spec_id": "TS-0042",
  "name": "inventory-system",
  "technology": "python",
  "python_version": "3.11",
  "waves": [
    {
      "number": 1,
      "tasks": [
        { "id": "task-001", "agent": "python-experts:django-expert" },
        { "id": "task-002", "agent": "python-experts:django-expert" }
      ],
      "validation": "from apps.users.models import User; print('Wave 1 OK')"
    },
    {
      "number": 2,
      "tasks": [
        { "id": "task-003", "agent": "python-experts:django-expert" }
      ],
      "validation": "from apps.orders.models import Order; print('Wave 2 OK')"
    }
  ],
  "metadata": {
    "tech_spec": "tech-specs/approved/TS-0042-inventory.md",
    "generated_at": "2025-01-15T10:00:00Z",
    "total_tasks": 3,
    "max_parallel": 2,
    "critical_path": ["task-001", "task-003"]
  }
}
```

## Best Practices

- **Spend time on decomposition**: Good decomposition is the multiplier
- **Contract-first**: Interfaces upfront prevent 80% of integration issues
- **Explicit boundaries**: Tell agents what they *cannot* touch
- **Small tasks**: Prefer more, smaller tasks (2-4 hours each)
- **Tech Spec first**: Create a Tech Spec before decomposition

## Anti-Patterns

- Tasks that share mutable state
- Circular dependencies between tasks
- Vague scope boundaries
- Missing contract definitions
- Skipping the integration phase

## Related Commands

| Command | Purpose |
|---------|---------|
| `/parallel-setup` | One-time project initialization |
| `/parallel-decompose` | Per-spec decomposition with prompts |
| `/parallel-run` | Execute and monitor parallel agents |
| `/parallel-integrate` | Post-execution verification |
| `/create-tech-spec` | Create Tech Spec before decomposition |
