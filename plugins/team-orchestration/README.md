# Team Orchestration Plugin

Dynamic task-based agentic delegation system for Product Forge with builder/validator pairs, self-validating hooks, and meta-prompt team coordination.

## Overview

The Team Orchestration plugin transforms software development with:

- **Task Coordination**: Native TaskCreate/Update/List/Get for structured task management
- **Builder/Validator Pairs**: Two-agent quality pattern for every domain
- **Self-Validation**: Embedded PostToolUse hooks run quality checks automatically
- **Meta-Prompts**: Template-driven team plan generation
- **Dynamic Adaptation**: Agents discover work, claim tasks, validate in real-time

## Architecture

```
Meta-Orchestration (/plan-with-team, /build-with-team)
        ↓
Task Coordination (TaskCreate/Update/List/Get)
        ↓
Builder Agents ↔ Validator Agents ↔ Existing Experts
        ↓
Validation Hooks (PostToolUse, SubagentStop)
```

## Quick Start

```bash
# Generate a team plan
/plan-with-team "user authentication feature"

# Execute with team coordination
/build-with-team

# Monitor progress
/team-status
```

## Components

### Builder Agents
Fast implementation agents that claim tasks and execute quickly:
- `django-builder` - Django models, views, serializers
- `react-builder` - React components and hooks
- `fastapi-builder` - FastAPI endpoints and services

### Validator Agents
Read-only quality assurance agents that enforce standards:
- `django-validator` - Type checking, linting, tests for Django
- `react-validator` - TypeScript, ESLint, tests for React
- `fastapi-validator` - Type checking, linting, tests for FastAPI

### Commands
- `/plan-with-team` - Generate implementation plan with agent assignments
- `/build-with-team` - Execute plan with Task coordination
- `/team-status` - Monitor current task execution progress

## Task Workflow

```
1. /plan-with-team creates task graph with TaskCreate
2. Builder claims task with TaskUpdate(owner, status="in_progress")
3. Builder implements (PostToolUse hooks validate on each change)
4. Builder completes with TaskUpdate(status="completed")
5. Validator claims validation task
6. Validator runs quality checks:
   - PASS: TaskUpdate(status="validated") → unblock next phase
   - FAIL: Create fix task → Builder re-claims
7. Repeat until all tasks validated
```

## Validation

### Automatic (PostToolUse Hooks)
- Runs on every Write/Edit by expert agents
- Non-blocking warnings in agent context
- Immediate feedback on code quality

### Explicit (Validator Agents)
- Runs comprehensive test suites
- Enforces quality gates between phases
- Creates fix tasks on failure

## Comparison with Parallel Framework

| Feature | Parallel Framework | Team Orchestration |
|---------|-------------------|-------------------|
| **Planning** | Contract-first PRD decomposition | Template-driven task generation |
| **Coordination** | Git worktrees + TodoWrite | TaskCreate/Update/List/Get |
| **Quality** | Manual validation in integration | Builder/validator pairs + hooks |
| **Execution** | Pre-planned parallel tracks | Dynamic task claiming |
| **Best For** | Large projects with clear contracts | Iterative development with quality gates |

Both systems coexist. Use parallel framework for contract-first decomposition, team orchestration for adaptive coordination.

## Development Status

- **Phase 0** (Week 1): ✅ Plugin structure created
- **Phase 1** (Weeks 2-4): 🚧 Builder/validator pairs in progress
- **Phase 2** (Weeks 5-7): ⏳ Self-validating hooks pending
- **Phase 3** (Weeks 8-9): ⏳ Meta-prompts and commands pending

## Documentation

- `docs/migration-from-parallel.md` - Migration guide from parallel framework
- `templates/team-plan-template.md` - Plan generation template
- Agent docs in `agents/` directory
- Validation scripts in `scripts/validation/`

## Contributing

When adding new builder/validator pairs:

1. Create `agents/{domain}-builder.md` with Task tools
2. Create `agents/{domain}-validator.md` with read-only tools
3. Add validation script `scripts/validation/validate-{domain}.sh`
4. Test full builder → validator → fix cycle
5. Update this README

## License

Same as Product Forge project.
