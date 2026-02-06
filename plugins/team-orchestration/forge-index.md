# Team Orchestration - Plugin Index

Dynamic task-based agentic delegation with builder/validator pairs and meta-prompt team orchestration.

## Skills

- `plan-with-team` - Generate team implementation plan with Task coordination

## Commands

- `/build-with-team` - Execute team plan with monitoring
- `/team-status` - Show current task execution status

## Builder Agents

Fast implementation agents that claim and execute tasks:

- `django-builder` - Django models, views, serializers, admin
- `react-builder` - React components, hooks, state management
- `fastapi-builder` - FastAPI endpoints, services, middleware

## Validator Agents

Read-only quality assurance agents with comprehensive checks:

- `django-validator` - Type checking (mypy), linting (ruff), tests, Django checks
- `react-validator` - TypeScript (tsc), linting (eslint), tests, build verification
- `fastapi-validator` - Type checking, linting, API tests, OpenAPI validation

## Key Concepts

### Task-Based Coordination
Uses native Claude Code Task tools (TaskCreate/Update/List/Get) for structured coordination between agents.

### Builder/Validator Pattern
Every task has two phases:
1. **Build Phase**: Builder agent implements feature quickly
2. **Validation Phase**: Validator agent runs quality checks

If validation fails, validator creates fix task and builder re-claims.

### Self-Validating Agents
Expert agents have PostToolUse hooks that run quality checks automatically on every code change. Non-blocking warnings keep workflow smooth.

## Workflow Example

```bash
# 1. Generate plan
/plan-with-team "user authentication with email verification"

# Creates task graph:
# - Task 1: User model (django-builder) [no dependencies]
# - Task 2: Validation (django-validator) [depends on Task 1]
# - Task 3: Auth endpoints (fastapi-builder) [depends on Task 2]
# - Task 4: Validation (fastapi-validator) [depends on Task 3]
# - Task 5: Login form (react-builder) [depends on Task 4]
# - Task 6: Validation (react-validator) [depends on Task 5]

# 2. Execute plan
/build-with-team

# Execution flow:
# - django-builder claims Task 1, implements User model
# - django-validator validates, passes → unblocks Task 3
# - fastapi-builder claims Task 3, implements endpoints
# - fastapi-validator validates, finds issue → creates fix task
# - fastapi-builder fixes issue, re-validates
# - react-builder claims Task 5 (now unblocked)
# - ... continues until all validated

# 3. Monitor
/team-status

# Shows:
# Phase 1: ✅ Complete (Tasks 1-2 validated)
# Phase 2: ⏳ In Progress (Task 4 fixing issues)
# Phase 3: ⏸ Blocked (waiting on Phase 2)
```

## Integration with Existing Plugins

Team orchestration works alongside existing Product Forge plugins:

- **Parallel Framework**: Use for contract-first decomposition, team orchestration for iterative work
- **Expert Agents**: Enhanced with PostToolUse validation hooks
- **Quality Tools**: Validation scripts call same tools (ruff, mypy, tsc, eslint)

## Development Phases

- **Phase 0** (Week 1): Plugin structure ← Current
- **Phase 1** (Weeks 2-4): Builder/validator pairs for Django, React, FastAPI
- **Phase 2** (Weeks 5-7): PostToolUse hooks in Python and TypeScript plugins
- **Phase 3** (Weeks 8-9): Meta-prompts and team commands
- **Phase 4** (Month 4+): Optional parallel framework deprecation notice

## See Also

- Full README: `plugins/team-orchestration/README.md`
- Migration guide: `docs/migration-from-parallel.md` (coming in Phase 4)
- Plan template: `templates/team-plan-template.md` (coming in Phase 3)
