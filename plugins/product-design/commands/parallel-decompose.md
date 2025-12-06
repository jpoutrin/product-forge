---
description: Break PRD into parallel task specs with contracts and dependency waves
argument-hint: <prd-file> [--tech-spec <ts-file>] [--output-dir <directory>]
---

# parallel-decompose

**Category**: Parallel Development

## Usage

```bash
/parallel-decompose <prd-file> [--tech-spec <ts-file>] [--output-dir <directory>]
```

## Arguments

- `<prd-file>`: Required - Path to PRD or FRD file to decompose
- `--tech-spec`: Optional - Path to Tech Spec file (TS-XXXX) to extract contracts and architecture from
- `--output-dir`: Optional - Task output directory (default: `.claude/tasks/`)

## Purpose

Analyze a PRD and decompose it into independent, parallel-executable task specifications. This is the critical decomposition phase that determines parallelization success.

> "The lead agent analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously." — Anthropic Multi-Agent Research

## Prerequisites

- Run `/parallel-setup` first
- Run `/parallel-ready-[tech]` and achieve score ≥80
- `.claude/` directory structure must exist
- (Recommended) Tech Spec exists with design decisions and contracts

## Document Flow

```
PRD (What to build)
    ↓
Tech Spec (How to build - optional but recommended)
    ↓
/parallel-decompose
    ↓
Tasks with boundaries from Tech Spec
```

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 0. Check for Tech Spec (if --tech-spec provided)

If Tech Spec is provided:
1. **Read Tech Spec** and extract:
   - Design Overview → `.claude/architecture.md`
   - Data Model → `.claude/contracts/types.py`
   - API Specification → `.claude/contracts/api-schema.yaml`
   - Component boundaries → Task ownership
   - RFC link (if any) → Task metadata

2. **Validate Tech Spec status**:
   - Must be APPROVED or REFERENCE
   - Warn if DRAFT (not ready for decomposition)

3. **Record linkage**:
   - Add `tech_spec_ref` to each generated task
   - Add Tech Spec path to `.claude/architecture.md`

If no Tech Spec provided:
- Generate contracts from PRD (existing behavior)
- Warn: "Consider creating a Tech Spec first for better contract definitions"

### 1. Read and Analyze PRD

Parse the PRD to extract:
- **Features/Epics**: Major functional areas
- **Technical Requirements**: API endpoints, data models, integrations
- **Dependencies**: What must be built before what
- **Integration Points**: Where components connect

### 2. Define Contracts First

> "For Contract-driven development to be successful, we need to take an API-first approach, where API providers and consumers collaboratively design and document the API specification first." — InfoQ

**If Tech Spec provided**: Extract contracts directly from Tech Spec sections:
- **Data Model section** → `types.py`
- **API Specification section** → `api-schema.yaml`

**If no Tech Spec**: Generate contracts from PRD (existing behavior).

**Update `.claude/contracts/types.py` (or `.ts`)**:

Extract shared types from PRD requirements:
```python
# .claude/contracts/types.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Entities from PRD
@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    name: str
    created_at: datetime

@dataclass(frozen=True)
class OrderDTO:
    id: int
    user_id: int
    total: int
    status: "OrderStatus"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
```

**Update `.claude/contracts/api-schema.yaml`**:

Define endpoints from PRD:
```yaml
openapi: 3.0.3
info:
  title: [Project] API
  version: 1.0.0

paths:
  /api/users/:
    get:
      summary: List users
      operationId: listUsers
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'

  /api/users/{id}/:
    get:
      summary: Get user by ID
      # ... full spec

components:
  schemas:
    User:
      type: object
      required: [id, email, name]
      properties:
        id: { type: integer }
        email: { type: string, format: email }
        name: { type: string }
```

### 3. Identify Task Boundaries

Analyze PRD to identify natural boundaries:

**For Django projects**:
- Each Django app = potential task boundary
- Each API resource = potential task
- Each feature area = potential task

**Boundary Rules**:
- Tasks should own specific files/directories
- No two tasks should modify the same file
- Dependencies should be one-way (no circular)
- Target 2-4 hours per task

### 4. Create Wave Plan

Organize tasks into waves based on dependencies:

```markdown
# .claude/task-graph.md

## Dependency Graph

```
Wave 1 (no dependencies - run in parallel)
├── task-001-users-app
├── task-002-products-app
└── task-003-shared-models

Wave 2 (depends on Wave 1 - run in parallel)
├── task-004-orders-app (needs users, products)
├── task-005-api-endpoints (needs all models)
└── task-006-admin-views (needs all models)

Wave 3 (depends on Wave 2 - run in parallel)
├── task-007-notifications (needs orders)
└── task-008-reports (needs all)

Wave 4 (sequential)
└── task-009-integration-tests (needs everything)
```

## Parallelization Summary

- **Total tasks**: 9
- **Parallel waves**: 4
- **Max concurrent agents**: 3
- **Critical path**: task-001 → task-004 → task-007 → task-009
```

### 5. Generate Task Specs

Create task files in `.claude/tasks/`:

**Naming convention**: `task-{NNN}-{component}-{feature}.md`

**Task template**:
```markdown
# Task: task-001-users-app

## Metadata

| Field | Value |
|-------|-------|
| ID | task-001 |
| Component | users |
| Feature | User management |
| Estimated Effort | 2-4 hours |
| Wave | 1 |
| Dependencies | None |
| Blocks | task-004, task-005, task-006 |
| Tech Spec | TS-XXXX (if provided) |
| RFC | RFC-XXXX (if linked via Tech Spec) |

## Scope

### Files to Create
- `apps/users/models.py`
- `apps/users/serializers.py`
- `apps/users/views.py`
- `apps/users/urls.py`
- `apps/users/tests/test_models.py`
- `apps/users/tests/test_views.py`
- `apps/users/tests/factories.py`

### Files to Modify
- `config/urls.py` (add users URLs)

### Boundary - DO NOT TOUCH
- `apps/orders/*` — owned by task-004
- `apps/products/*` — owned by task-002
- `apps/*/migrations/*` — handle post-integration
- `.claude/contracts/*` — read-only

## Contracts (Read-Only)

Reference these contracts but do not modify:
- `.claude/contracts/types.py` — UserDTO definition
- `.claude/contracts/api-schema.yaml` — /api/users/* endpoints

## Requirements

### Functional
1. User model with email-based authentication
2. UserSerializer with explicit fields (no `__all__`)
3. UserViewSet with list, retrieve, create, update actions
4. Email uniqueness validation

### Non-Functional
1. All endpoints typed (request/response)
2. >80% test coverage for new code
3. mypy passes with no errors
4. ruff check passes

## Acceptance Criteria

- [ ] User model matches UserDTO in contracts
- [ ] API endpoints match OpenAPI spec exactly
- [ ] All tests pass: `pytest apps/users/`
- [ ] Type check passes: `mypy apps/users/`
- [ ] Lint passes: `ruff check apps/users/`
- [ ] No files modified outside scope
- [ ] No migrations created (defer to integration)

## Implementation Notes

- Use Factory Boy for test fixtures
- Follow CLAUDE.md conventions
- Reference existing patterns in codebase
```

### 6. Update Architecture Doc

Update `.claude/architecture.md` with component ownership:

```markdown
# System Architecture

## Overview
[From PRD summary]

## Components

| Component | App/Module | Owner Task | Dependencies |
|-----------|------------|------------|--------------|
| User Management | apps/users/ | task-001 | None |
| Product Catalog | apps/products/ | task-002 | None |
| Order Processing | apps/orders/ | task-004 | task-001, task-002 |
| API Layer | apps/api/ | task-005 | task-001, task-002, task-003 |

## Boundaries

Each task owns specific directories. No cross-boundary modifications allowed during parallel execution.

## Integration Points

Integration happens in Wave 4 after all parallel work completes:
1. Migration merge
2. Integration tests
3. Contract compliance verification
```

### 7. Validate Decomposition

Check for issues:
- [ ] No file ownership conflicts between tasks
- [ ] No circular dependencies in wave graph
- [ ] All contract references exist
- [ ] Each task is 2-4 hours estimated
- [ ] Dependencies are achievable (no impossible orderings)

### 8. Report Results

Output:
```
📦 PRD Decomposition Complete

Source: docs/user-orders-prd.md
Tasks Generated: 9

Wave Summary:
┌───────┬─────────┬───────────────────────────────────────────┐
│ Wave  │ Tasks   │ Description                               │
├───────┼─────────┼───────────────────────────────────────────┤
│ 1     │ 3       │ Core models (users, products, shared)     │
│ 2     │ 3       │ Business logic (orders, API, admin)       │
│ 3     │ 2       │ Features (notifications, reports)         │
│ 4     │ 1       │ Integration tests                         │
└───────┴─────────┴───────────────────────────────────────────┘

Max Parallel Agents: 3
Estimated Total Time: 8-12 hours (vs 24-36 sequential)

Files Created:
✅ .claude/tasks/task-001-users-app.md
✅ .claude/tasks/task-002-products-app.md
... (9 tasks total)
✅ .claude/task-graph.md
✅ .claude/contracts/types.py (updated)
✅ .claude/contracts/api-schema.yaml (updated)
✅ .claude/architecture.md (updated)

Next steps:
1. Review task specs in .claude/tasks/
2. Verify contracts are complete
3. Run /parallel-prompts to generate agent commands
```

## Example

```bash
# Decompose PRD with Tech Spec (recommended)
/parallel-decompose docs/inventory-prd.md --tech-spec tech-specs/approved/TS-0042-inventory-system.md

# Decompose PRD only (generates contracts from PRD)
/parallel-decompose docs/inventory-prd.md

# Decompose with custom output
/parallel-decompose docs/auth-frd.md --tech-spec tech-specs/approved/TS-0015-auth.md --output-dir ./parallel-tasks/

# After decomposition, generate prompts
/parallel-prompts
```

## Key Principles

1. **Contract-first**: Define types and API schemas before tasks
2. **Explicit boundaries**: Each task owns specific files
3. **2-4 hour granularity**: Not too big, not too small
4. **One-way dependencies**: No circular task dependencies
5. **Wave organization**: Maximize parallel execution

## Related Commands

- `/parallel-setup` - Create infrastructure first
- `/parallel-ready-[tech]` - Verify readiness (score ≥80)
- `/parallel-prompts` - Generate agent prompts from tasks
- `/parallel-integrate` - Verify integration after execution
