---
name: parallel-agents
short: Decompose PRDs into parallel agent tasks
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
when: User wants to parallelize development, run multiple agents simultaneously, decompose a PRD into independent tasks, scale work across concurrent workstreams, or coordinate multi-agent workflows
---

# Parallel Agent Development

Orchestrate massively parallel development by decomposing work into independent tasks that multiple Claude Code instances can execute simultaneously.

## Workflow Overview

```
/parallel-setup       → One-time: creates parallel/ directory
         ↓
/parallel-decompose   → Per Tech Spec: creates TS-XXXX-slug/ with all artifacts
         ↓
[Run Claude agents in parallel using generated scripts]
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
│       │   ├── launch-wave-1.sh
│       │   ├── launch-wave-2.sh
│       │   └── monitor.sh
│       └── integration-report.md       # Post-execution report
├── tech-specs/                         # Source Tech Specs
│   └── approved/TS-XXXX-slug.md
└── CLAUDE.md                           # Project conventions
```

## manifest.json

Tracks regeneration metadata for each decomposition:

```json
{
  "version": "1.0.0",
  "created_at": "2025-12-07T14:30:00Z",
  "tech_spec": {
    "id": "TS-0042",
    "title": "inventory-system",
    "path": "tech-specs/approved/TS-0042-inventory-system.md",
    "status": "APPROVED"
  },
  "sources": {
    "prd": "docs/prds/inventory-prd.md",
    "tech_spec": "tech-specs/approved/TS-0042-inventory-system.md"
  },
  "technology": "django",
  "tasks": { "total": 6, "waves": 3, "files": [...] },
  "integration": { "status": "pending" }
}
```

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

Launch multiple Claude Code instances with isolated scope.

### Agent Permissions

Sub-agents need write permissions:

| Strategy | When to Use |
|----------|-------------|
| `--dangerously-skip-permissions` | Isolated worktrees (safe) |
| `--allowedTools "Edit(/src/auth/**)"` | Shared workspace, path-scoped |

See `references/claude-code-tools.md` for full tool list and permission syntax.

### Isolation Strategies

**Git worktrees** (recommended):
```bash
git worktree add ../workspace-task-001 -b feature/task-001-users
```

**Directory boundaries**: Assign each agent to specific directories.

**Branch-per-task**: Each agent on dedicated branch.

See `references/execution-patterns.md` for automation scripts.

### Launching Agents

Use generated scripts:

```bash
# Run the launch script
./parallel/TS-0042-inventory-system/scripts/launch-wave-1.sh

# Or manually in separate terminals
cd ../workspace-task-001
claude --dangerously-skip-permissions --print "$(cat parallel/TS-0042-inventory-system/prompts/task-001.txt)"
```

### Monitor Progress

```bash
./parallel/TS-0042-inventory-system/scripts/monitor.sh
```

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

### Launch Agents
```bash
# Using generated scripts
./parallel/TS-0042-inventory-system/scripts/launch-wave-1.sh

# Or with git worktrees
git worktree add ../workspace-task-001 -b feature/task-001
cd ../workspace-task-001
claude --dangerously-skip-permissions --print "$(cat parallel/TS-0042-inventory-system/prompts/task-001.txt)"
```

### Integration Check
```bash
/parallel-integrate --parallel-dir parallel/TS-0042-inventory-system
```

### View Results
```bash
cat parallel/TS-0042-inventory-system/integration-report.md
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `/parallel-setup` | One-time project initialization |
| `/parallel-decompose` | Per-spec decomposition with prompts |
| `/parallel-integrate` | Post-execution verification |
| `/create-tech-spec` | Create Tech Spec before decomposition |
