# Parallel Agent Development

**Guidelines for massively parallelizing development with multiple Claude Code agents**

Version: 1.0.0

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
│                        PREPARATION                              │
│  /parallel-setup → /parallel-ready → /parallel-fix             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DECOMPOSITION                             │
│  /parallel-decompose docs/prd.md                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        EXECUTION                                │
│  /parallel-prompts → [Run Agents] → /parallel-integrate         │
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

---

## Phase 1: Preparation

**Goal**: Ensure the codebase can support parallel development without conflicts.

### Step 1.1: Initialize Infrastructure

```bash
/parallel-setup
```

Creates:
```
.claude/
├── tasks/              # Task specifications
├── contracts/          # Shared interfaces (types, OpenAPI)
├── architecture.md     # System design
└── readiness-report.md # Assessment results
```

### Step 1.2: Assess Readiness

```bash
/parallel-ready-django    # For Django projects
/parallel-ready-ts        # For TypeScript projects (future)
```

**Scoring dimensions** (100 points total):
| Dimension | Weight | What to Check |
|-----------|--------|---------------|
| Module Boundaries | 20 | Directory separation, cross-imports |
| Shared State | 20 | Global variables, signals, singletons |
| Interface Contracts | 20 | Types, OpenAPI specs, typed boundaries |
| Test Infrastructure | 15 | Test framework, coverage, CI |
| Documentation | 15 | CLAUDE.md, conventions, architecture |
| Dependencies | 10 | Lock files, clean dependency tree |

**Thresholds**:
- **≥80**: Ready for parallelization
- **50-79**: Fix high-priority issues first
- **<50**: Significant restructuring needed

### Step 1.3: Fix Blockers

```bash
/parallel-fix-django    # For Django projects
```

Common blockers and fixes:

| Blocker | Fix |
|---------|-----|
| Circular dependencies | Extract shared code to common module |
| God modules | Split by domain/feature |
| Missing contracts | Add typed interfaces + OpenAPI spec |
| No CLAUDE.md | Create with actual codebase patterns |
| Global state | Convert to injectable services |

---

## Phase 2: Decomposition

**Goal**: Break the PRD into parallel-executable task specs with shared contracts.

> "The lead agent analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously." — Anthropic

### Step 2.1: Decompose PRD

```bash
/parallel-decompose docs/prd.md
```

**Creates**:
- `.claude/contracts/types.py` - Shared domain types
- `.claude/contracts/api-schema.yaml` - OpenAPI specification
- `.claude/tasks/task-*.md` - Individual task specs
- `.claude/task-graph.md` - Dependency visualization

### Step 2.2: Contract-First Design

> "For Contract-driven development to be successful, we need to take an API-first approach." — InfoQ

**Define contracts BEFORE tasks**:

```python
# .claude/contracts/types.py
@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    name: str
```

```yaml
# .claude/contracts/api-schema.yaml
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

### Step 2.3: Task Spec Format

Each task file in `.claude/tasks/`:

```markdown
# Task: task-001-users-app

## Metadata
- Effort: 2-4 hours
- Wave: 1
- Dependencies: None

## Scope
### Create/Modify
- apps/users/**

### Boundary (DO NOT TOUCH)
- apps/orders/* — owned by task-002
- */migrations/* — post-integration

## Contracts
- .claude/contracts/types.py
- .claude/contracts/api-schema.yaml

## Acceptance Criteria
- [ ] Endpoints match OpenAPI spec
- [ ] Tests pass with >80% coverage
- [ ] Type checks pass
```

### Step 2.4: Wave Planning

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

### Step 3.1: Generate Prompts

```bash
/parallel-prompts
```

Creates `.claude/agent-prompts.md` with:
- Worktree setup commands per task
- Copy-paste prompts for each agent
- Execution scripts for automation

### Step 3.2: Create Isolated Workspaces

**Git Worktrees (Recommended)**:
```bash
git worktree add ../workspace-task-001 -b feature/task-001
git worktree add ../workspace-task-002 -b feature/task-002
git worktree add ../workspace-task-003 -b feature/task-003
```

Each workspace gets:
- Own filesystem
- Own git branch
- Shared contracts (read-only)
- Same CLAUDE.md

### Step 3.3: Launch Agents

Open multiple terminals and launch:

```bash
# Terminal 1
cd ../workspace-task-001
claude "[paste prompt from agent-prompts.md]"

# Terminal 2
cd ../workspace-task-002
claude "[paste prompt from agent-prompts.md]"

# Terminal 3
cd ../workspace-task-003
claude "[paste prompt from agent-prompts.md]"
```

### Step 3.4: Integrate Results

After all Wave N agents complete:

```bash
# Merge branches
git checkout main
git merge feature/task-001
git merge feature/task-002
git merge feature/task-003

# Run integration check
/parallel-integrate
```

---

## Phase 4: Integration

**Goal**: Verify all parallel work integrates correctly.

```bash
/parallel-integrate
```

**Checks**:
1. **Contract compliance** — Do implementations match specs?
2. **Boundary compliance** — Did agents stay in scope?
3. **Migration merge** (Django) — `makemigrations --merge`
4. **Test suite** — All tests pass?
5. **Type check** — No type errors?

**Output**: `.claude/integration-report.md`

---

## Commands Reference

| Command | Phase | Purpose |
|---------|-------|---------|
| `/parallel-setup` | 1 | Initialize .claude/ infrastructure |
| `/parallel-ready-django` | 1 | Assess Django codebase readiness |
| `/parallel-fix-django` | 1 | Fix Django-specific blockers |
| `/parallel-decompose <prd>` | 2 | Break PRD into task specs |
| `/parallel-prompts` | 3 | Generate agent execution prompts |
| `/parallel-integrate` | 4 | Verify integration after execution |

---

## File Structure

After full workflow:

```
project/
├── .claude/
│   ├── contracts/
│   │   ├── types.py           # Shared domain types
│   │   └── api-schema.yaml    # OpenAPI specification
│   ├── tasks/
│   │   ├── task-001-*.md
│   │   ├── task-002-*.md
│   │   └── ...
│   ├── architecture.md        # System design
│   ├── readiness-report.md    # Assessment results
│   ├── task-graph.md          # Dependency visualization
│   ├── agent-prompts.md       # Execution prompts
│   └── integration-report.md  # Post-execution report
├── CLAUDE.md                  # Project conventions
└── src/ or apps/              # Source code
```

---

## Best Practices

### Do

- **Spend time on decomposition** — Good decomposition is the multiplier
- **Contract-first** — Interfaces upfront prevent 80% of integration issues
- **Explicit boundaries** — Tell agents what they *cannot* touch
- **Small tasks** — Prefer more, smaller tasks (2-4 hours each)
- **Wave planning** — Maximize parallel execution

### Don't

- Tasks that share mutable state
- Circular dependencies between tasks
- Vague scope boundaries
- Missing contract definitions
- Skipping the integration phase

---

## Sources

| Document | Source | Key Takeaway |
|----------|--------|--------------|
| Multi-Agent Research System | Anthropic | 90% performance improvement with multi-agent |
| Building Effective Agents | Anthropic | Orchestrator-worker pattern |
| Claude Code Best Practices | Anthropic | "Most powerful applications involve running multiple Claude instances in parallel" |
| Contract-Driven Development | InfoQ | API-first enables parallel team work |
