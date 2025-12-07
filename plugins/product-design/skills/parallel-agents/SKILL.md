---
name: parallel-agents
short: Decompose PRDs into parallel agent tasks
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
/parallel-setup       → One-time: creates parallel/ directory
         ↓
/parallel-decompose   → Per Tech Spec: creates TS-XXXX-slug/ with all artifacts
         ↓
/parallel-run         → Delegates to `cpo run` for execution
         ↓
/parallel-integrate   → Verify & generate integration report
```

## Directory Structure

Each decomposition creates an isolated artifact folder keyed by Tech Spec:

```
project/
├── parallel/                           # Created by /parallel-setup (one-time)
│   ├── README.md
│   ├── .gitignore
│   └── TS-XXXX-{slug}/                 # Created by /parallel-decompose
│       ├── manifest.json               # Regeneration metadata
│       ├── context.md                  # Shared project context (token-efficient)
│       ├── architecture.md             # System design from Tech Spec
│       ├── task-graph.md               # Dependency visualization (Mermaid flowchart)
│       ├── contracts/
│       │   ├── types.py (or types.ts)  # Shared domain types
│       │   └── api-schema.yaml         # OpenAPI specification
│       ├── tasks/
│       │   ├── task-001-users.md       # Compact YAML format
│       │   ├── task-002-products.md
│       │   └── ...
│       ├── prompts/
│       │   ├── agent-prompts.md        # All launch commands
│       │   └── task-*.txt              # Individual agent prompts
│       ├── scripts/
│       │   ├── run-parallel.sh         # Main orchestrator (from /parallel-run)
│       │   ├── launch-wave-1.sh
│       │   ├── launch-wave-2.sh
│       │   └── monitor-live.sh
│       └── integration-report.md       # Post-execution report
├── tech-specs/                         # Source Tech Specs
│   └── approved/TS-XXXX-slug.md
└── CLAUDE.md                           # Project conventions
```

## manifest.json (cpo format)

The `cpo` tool requires a specific manifest format with wave definitions:

```json
{
  "tech_spec_id": "TS-0042",
  "waves": [
    {
      "number": 1,
      "tasks": [
        {
          "id": "task-001-users",
          "agent": "python-experts:django-expert",
          "prompt_file": "prompts/task-001.txt"
        },
        {
          "id": "task-002-products",
          "agent": "python-experts:django-expert",
          "prompt_file": "prompts/task-002.txt"
        }
      ],
      "validation": "python -c 'from apps.users.models import User'"
    },
    {
      "number": 2,
      "tasks": [
        {
          "id": "task-004-orders",
          "agent": "python-experts:django-expert",
          "prompt_file": "prompts/task-004.txt"
        }
      ],
      "validation": "pytest apps/orders/tests/ -v"
    }
  ]
}
```

**Key fields:**
- `tech_spec_id`: Links to Tech Spec for traceability
- `waves[].number`: Wave execution order (1, 2, 3...)
- `waves[].tasks[].id`: Unique task identifier
- `waves[].tasks[].agent`: Agent type (e.g., `python-experts:django-expert`)
- `waves[].tasks[].prompt_file`: Path to task prompt file
- `waves[].validation`: Optional command to validate wave completion

## Phase 1: Setup (One-Time)

Run once per project to create the parallel development infrastructure:

```bash
/parallel-setup [--tech django|typescript|go]
```

Creates:
- `parallel/` directory at project root
- `parallel/README.md` - Explains the workflow
- `parallel/.gitignore` - What to track vs ignore

## Phase 2: Decomposition

Decompose a PRD into parallel-executable tasks:

```bash
# With Tech Spec (recommended)
/parallel-decompose docs/prd.md --tech-spec tech-specs/approved/TS-0042-inventory.md

# Without Tech Spec (fallback)
/parallel-decompose docs/prd.md --name my-feature --tech django
```

Creates `parallel/TS-XXXX-slug/` with:
- **manifest.json** - Regeneration metadata
- **context.md** - Shared project context (read once by all agents)
- **contracts/** - types.py, api-schema.yaml
- **tasks/** - Compact YAML task specs
- **prompts/** - Agent launch commands and individual prompts
- **scripts/** - launch-wave-N.sh, monitor.sh

### Decomposition Principles

- **Contract-first**: Define interfaces before implementation
- **Maximize independence**: Tasks should touch separate files/modules
- **Explicit boundaries**: Specify what each task CAN and CANNOT touch
- **2-4 hour granularity**: Not too big, not too small
- **Token efficiency**: Compact YAML format, shared context.md

### Task Spec Format (Compact YAML)

```yaml
---
id: task-001
component: users
wave: 1
deps: []
blocks: [task-004, task-005]
agent: django-expert
tech_spec: TS-0042
contracts: [contracts/types.py, contracts/api-schema.yaml]
---
# task-001: User Management

## Scope
CREATE: apps/users/{models,views,serializers,urls}.py, apps/users/tests/*.py
MODIFY: config/urls.py
BOUNDARY: apps/orders/*, apps/products/*, apps/*/migrations/*

## Requirements
- User model with email authentication
- UserSerializer with explicit fields
- UserViewSet (list, retrieve, create, update)

## Checklist
- [ ] Model matches UserDTO in contracts/types.py
- [ ] API matches /api/users/* in contracts/api-schema.yaml
- [ ] pytest apps/users/ passes
- [ ] mypy apps/users/ passes
```

See `references/task-template.md` for full specification.

## Phase 3: Parallel Execution

Execute parallel agents using the `/parallel-run` command or `cpo` directly:

### Using /parallel-run (delegates to cpo)

```bash
# Execute parallel agents
/parallel-run parallel/TS-0042-inventory-system/

# Validate only (no execution)
/parallel-run parallel/TS-0042-inventory-system/ --validate

# Check status of ongoing/completed execution
/parallel-run parallel/TS-0042-inventory-system/ --status
```

### Using cpo directly

```bash
# Validate manifest structure
cpo validate parallel/TS-0042-inventory-system/

# Execute parallel agents
cpo run parallel/TS-0042-inventory-system/

# Check execution status
cpo status parallel/TS-0042-inventory-system/
```

### What `cpo run` Does

1. Validates manifest.json structure and prompts
2. Creates git worktrees for each task
3. Launches agents in parallel (respects wave dependencies)
4. Monitors progress with live output
5. Generates logs in `$PARALLEL_DIR/logs/`
6. Creates report in `$PARALLEL_DIR/report.json`

### Agent Permissions

Sub-agents run with `--dangerously-skip-permissions` because they're isolated in worktrees.

## Phase 4: Integration

After all agents complete:

```bash
/parallel-integrate --parallel-dir parallel/TS-0042-inventory-system
```

Checks:
1. **Contract compliance** - Do implementations match specs?
2. **Boundary compliance** - Did agents stay in scope?
3. **Tech Spec compliance** - Does implementation match design?
4. **Migration merge** (Django) - `makemigrations --merge`
5. **Test suite** - All tests pass?
6. **Type check** - No type errors?

Output: `parallel/TS-0042-inventory-system/integration-report.md`

## Best Practices

- **Spend time on decomposition**: Good decomposition is the multiplier
- **Contract-first**: Interfaces upfront prevent 80% of integration issues
- **Explicit boundaries**: Tell agents what they *cannot* touch
- **Small tasks**: Prefer more, smaller tasks (2-4 hours each)
- **Tech Spec first**: Create a Tech Spec before decomposition for better contracts

## Anti-Patterns

- Tasks that share mutable state
- Circular dependencies between tasks
- Vague scope boundaries
- Missing contract definitions
- Skipping the integration phase

## Quick Reference

### One-Time Setup
```bash
/parallel-setup --tech django
```

### Decompose PRD
```bash
/parallel-decompose docs/prd.md --tech-spec tech-specs/approved/TS-0042-inventory.md
```

### Execute Agents
```bash
# Using /parallel-run (delegates to cpo)
/parallel-run parallel/TS-0042-inventory-system/

# Using cpo directly
cpo run parallel/TS-0042-inventory-system/
```

### Check Status
```bash
# Using /parallel-run
/parallel-run parallel/TS-0042-inventory-system/ --status

# Using cpo directly
cpo status parallel/TS-0042-inventory-system/
```

### Integration Check
```bash
/parallel-integrate --parallel-dir parallel/TS-0042-inventory-system
```

### View Results
```bash
cat parallel/TS-0042-inventory-system/report.json
cat parallel/TS-0042-inventory-system/integration-report.md
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `/parallel-setup` | One-time project initialization |
| `/parallel-decompose` | Per-spec decomposition with prompts |
| `/parallel-run` | Execute and monitor parallel agents |
| `/parallel-integrate` | Post-execution verification |
| `/create-tech-spec` | Create Tech Spec before decomposition |
