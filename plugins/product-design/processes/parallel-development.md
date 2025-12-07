# Parallel Agent Development

**Guidelines for massively parallelizing development with multiple Claude Code agents**

Version: 2.0.0

---

## Overview

Parallel agent development is a methodology for breaking down large development tasks into independent work units that multiple Claude Code instances can execute simultaneously.

**Key Benefits**:
- 90% performance improvement over single-agent (Anthropic research)
- 90% reduction in development time for complex queries
- Better token utilization through separate contexts

> "Multi-agent systems work mainly because they help spend enough tokens to solve the problem. Token usage by itself explains 80% of the variance."
> — Anthropic Engineering Blog

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     PREPARATION (One-Time)                       │
│  /parallel-setup → creates parallel/ directory                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DECOMPOSITION                              │
│  /parallel-decompose prd.md --tech-spec TS-XXXX.md               │
│  Creates: parallel/TS-XXXX-slug/ with all artifacts              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        EXECUTION                                 │
│  Run generated scripts → [Parallel Agents] → /parallel-integrate │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

| Principle | Description | Source |
|-----------|-------------|--------|
| **Contract-First** | Define interfaces before implementation | Industry best practice |
| **Isolated Contexts** | Each agent gets its own workspace | Anthropic multi-agent research |
| **Explicit Boundaries** | Tasks specify what they CAN and CANNOT touch | Anthropic tool design guidance |
| **Orchestrator-Worker** | One agent decomposes, many execute | Anthropic "Building Effective Agents" |
| **Token Efficiency** | Compact tasks, shared context.md | Minimize agent context size |

---

## Phase 1: Preparation (One-Time)

**Goal**: Initialize parallel development infrastructure in the project.

```bash
/parallel-setup [--tech django|typescript|go]
```

Creates:
```
parallel/
├── README.md           # Explains parallel development workflow
└── .gitignore          # What to track vs ignore
```

This is a one-time setup per project.

---

## Phase 2: Decomposition

**Goal**: Break the PRD into parallel-executable task specs with shared contracts.

> "The lead agent analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously." — Anthropic

### Step 2.1: Create Tech Spec (Recommended)

Before decomposing, create a Tech Spec that defines design decisions:

```bash
/create-tech-spec inventory-system
```

This creates `tech-specs/approved/TS-XXXX-inventory-system.md` with:
- Design overview
- Data model definitions
- API specifications
- Component boundaries

### Step 2.2: Decompose PRD

```bash
# With Tech Spec (recommended)
/parallel-decompose docs/prd.md --tech-spec tech-specs/approved/TS-0042-inventory.md

# Without Tech Spec (fallback)
/parallel-decompose docs/prd.md --name my-feature --tech django
```

**Creates** in `parallel/TS-XXXX-slug/`:

| Artifact | Purpose |
|----------|---------|
| `manifest.json` | Regeneration metadata and traceability |
| `context.md` | Shared project context (read once by all agents) |
| `contracts/types.py` | Shared domain types |
| `contracts/api-schema.yaml` | OpenAPI specification |
| `tasks/task-*.md` | Compact YAML task specs |
| `prompts/agent-prompts.md` | All launch commands in one place |
| `prompts/task-*.txt` | Individual agent prompts |
| `scripts/launch-wave-N.sh` | Automation scripts per wave |
| `scripts/monitor.sh` | Progress monitoring |
| `architecture.md` | System design |
| `task-graph.md` | Dependency visualization (Mermaid flowchart) |

### Step 2.3: Contract-First Design

> "For Contract-driven development to be successful, we need to take an API-first approach." — InfoQ

**Define contracts BEFORE tasks** (from Tech Spec or PRD):

```python
# parallel/TS-XXXX-slug/contracts/types.py
@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    name: str
```

```yaml
# parallel/TS-XXXX-slug/contracts/api-schema.yaml
paths:
  /api/users/{id}/:
    get:
      summary: Get user by ID
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

### Step 2.4: Task Spec Format (Compact YAML)

Each task in `parallel/TS-XXXX-slug/tasks/`:

```yaml
---
id: task-001
component: users
wave: 1
deps: []
blocks: [task-004]
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
- User model with email auth
- UserSerializer (explicit fields, no __all__)
- UserViewSet (list, retrieve, create, update)

## Checklist
- [ ] Model matches UserDTO in contracts/types.py
- [ ] API matches /api/users/* in contracts/api-schema.yaml
- [ ] pytest apps/users/ passes
- [ ] mypy apps/users/ passes
```

### Step 2.5: Wave Planning

Organize tasks into dependency waves:

```
Wave 1 (parallel)     Wave 2 (parallel)     Wave 3
─────────────────     ─────────────────     ─────────
task-001-users   ───► task-004-orders ──►
task-002-products───► task-005-api    ──► task-007-integration
task-003-shared  ───► task-006-tests  ──►
```

---

## Phase 3: Execution

**Goal**: Run multiple Claude Code agents in parallel with isolated workspaces.

### Step 3.1: Create Isolated Workspaces

**Git Worktrees (Recommended)**:
```bash
git worktree add ../workspace-task-001 -b feature/task-001-users
git worktree add ../workspace-task-002 -b feature/task-002-products
git worktree add ../workspace-task-003 -b feature/task-003-shared
```

Each workspace gets:
- Own filesystem
- Own git branch
- Shared contracts (read-only)
- Same CLAUDE.md

### Step 3.2: Launch Agents

**Using generated scripts**:
```bash
./parallel/TS-0042-inventory-system/scripts/launch-wave-1.sh
```

**Or manually** in multiple terminals:

```bash
# Terminal 1
cd ../workspace-task-001
claude --dangerously-skip-permissions --print "$(cat parallel/TS-0042-inventory-system/prompts/task-001.txt)"

# Terminal 2
cd ../workspace-task-002
claude --dangerously-skip-permissions --print "$(cat parallel/TS-0042-inventory-system/prompts/task-002.txt)"

# Terminal 3
cd ../workspace-task-003
claude --dangerously-skip-permissions --print "$(cat parallel/TS-0042-inventory-system/prompts/task-003.txt)"
```

### Step 3.3: Monitor Progress

```bash
./parallel/TS-0042-inventory-system/scripts/monitor.sh
```

### Step 3.4: Merge Results

After all Wave N agents complete:

```bash
# Merge branches
git checkout main
git merge feature/task-001-users
git merge feature/task-002-products
git merge feature/task-003-shared

# Then launch Wave N+1
./parallel/TS-0042-inventory-system/scripts/launch-wave-2.sh
```

---

## Phase 4: Integration

**Goal**: Verify all parallel work integrates correctly.

```bash
/parallel-integrate --parallel-dir parallel/TS-0042-inventory-system
```

**Checks**:
1. **Contract compliance** — Do implementations match specs?
2. **Boundary compliance** — Did agents stay in scope?
3. **Tech Spec compliance** — Does implementation match design?
4. **Migration merge** (Django) — `makemigrations --merge`
5. **Test suite** — All tests pass?
6. **Type check** — No type errors?

**Output**: `parallel/TS-0042-inventory-system/integration-report.md`

---

## Commands Reference

| Command | Phase | Purpose |
|---------|-------|---------|
| `/parallel-setup` | 1 | One-time: create parallel/ directory |
| `/parallel-decompose <prd> --tech-spec <ts>` | 2 | Per-spec: create TS-XXXX-slug/ with all artifacts |
| `/parallel-integrate [--parallel-dir]` | 4 | Verify integration after execution |
| `/create-tech-spec` | (Pre) | Create Tech Spec before decomposition |

---

## File Structure

After full workflow:

```
project/
├── parallel/
│   ├── README.md                       # Workflow documentation
│   ├── .gitignore
│   └── TS-0042-inventory-system/       # Per Tech Spec
│       ├── manifest.json               # Regeneration metadata
│       ├── context.md                  # Shared project context
│       ├── contracts/
│       │   ├── types.py                # Shared domain types
│       │   └── api-schema.yaml         # OpenAPI specification
│       ├── tasks/
│       │   ├── task-001-users.md
│       │   ├── task-002-products.md
│       │   └── ...
│       ├── prompts/
│       │   ├── agent-prompts.md        # All launch commands
│       │   └── task-*.txt              # Individual prompts
│       ├── scripts/
│       │   ├── launch-wave-1.sh
│       │   ├── launch-wave-2.sh
│       │   └── monitor.sh
│       ├── architecture.md             # System design
│       ├── task-graph.md               # Dependency visualization (Mermaid flowchart)
│       └── integration-report.md       # Post-execution report
├── tech-specs/
│   └── approved/TS-0042-inventory-system.md
├── CLAUDE.md                           # Project conventions
└── src/ or apps/                       # Source code
```

---

## manifest.json Schema

Each decomposition tracks metadata for regeneration:

```json
{
  "version": "1.0.0",
  "created_at": "2025-12-07T14:30:00Z",
  "updated_at": "2025-12-07T15:00:00Z",
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
  "command": {
    "name": "parallel-decompose",
    "args": { "prd": "...", "tech_spec": "...", "tech": "django" },
    "invoked_at": "2025-12-07T14:30:00Z"
  },
  "technology": "django",
  "tasks": {
    "total": 9,
    "waves": 4,
    "files": ["tasks/task-001-users.md", "..."]
  },
  "integration": {
    "status": "pending",
    "report_path": null,
    "completed_at": null
  }
}
```

---

## Best Practices

### Do

- **Spend time on decomposition** — Good decomposition is the multiplier
- **Tech Spec first** — Create Tech Spec before decomposition for better contracts
- **Contract-first** — Interfaces upfront prevent 80% of integration issues
- **Explicit boundaries** — Tell agents what they *cannot* touch
- **Small tasks** — Prefer more, smaller tasks (2-4 hours each)
- **Wave planning** — Maximize parallel execution
- **Use generated scripts** — Automation reduces errors

### Don't

- Tasks that share mutable state
- Circular dependencies between tasks
- Vague scope boundaries
- Missing contract definitions
- Skipping the integration phase
- Modifying contracts during parallel execution

---

## Token Efficiency

### Compact Task Format
Tasks use YAML frontmatter + bullet lists to minimize token usage:
- Frontmatter for metadata (YAML)
- Scope section with glob patterns
- Bullet list requirements
- Checkbox checklist

### Shared context.md
Each agent reads `context.md` once instead of duplicating project info in every task.

### File Reference Prompts
Prompts reference files instead of embedding content:
```
Execute task from parallel/TS-0042/tasks/task-001.md.
Read context from parallel/TS-0042/context.md first.
```

---

## Sources

| Document | Source | Key Takeaway |
|----------|--------|--------------|
| Multi-Agent Research System | Anthropic | 90% performance improvement with multi-agent |
| Building Effective Agents | Anthropic | Orchestrator-worker pattern |
| Claude Code Best Practices | Anthropic | "Most powerful applications involve running multiple Claude instances in parallel" |
| Contract-Driven Development | InfoQ | API-first enables parallel team work |
