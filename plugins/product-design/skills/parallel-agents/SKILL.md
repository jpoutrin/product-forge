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
PRD --> Decomposition --> Contracts --> Task Specs --> Parallel Execution --> Integration
```

## Phase 1: Setup Project Structure

Create the orchestration directory:

```
project/
  .claude/
    prd.md                    # Original PRD
    architecture.md           # System architecture decisions
    tasks/                    # Individual task specs
      task-001-*.md
      ...
    contracts/                # Shared interfaces
      api-schema.yaml
      types.ts
  src/
```

## Phase 2: Decomposition (Single Agent)

Analyze the PRD and generate parallelizable tasks. Key outputs:

1. **Architecture doc** - System design, component boundaries, data flow
2. **Contracts** - API schemas, type definitions, interface contracts
3. **Task specs** - Independent work units with clear scope

### Decomposition Principles

- Maximize independence: tasks should touch separate files/modules
- Define interfaces first: contracts prevent integration failures
- Identify sequential dependencies: flag tasks that must wait
- Aim for 2-4 hour task granularity

### Task Spec Template

See `references/task-template.md` for the standard task specification format.

## Phase 3: Contract Definition

Before parallel execution, establish shared contracts:

**API Contracts** (OpenAPI/GraphQL):
- Endpoint signatures, request/response schemas, error formats

**Type Contracts** (TypeScript/language-specific):
- Shared domain types, interface definitions, enum values

**Convention Contracts** (CLAUDE.md):
- Code style, error handling patterns, logging format, test conventions

## Phase 4: Parallel Execution

Launch multiple Claude Code instances with isolated scope:

```bash
claude "Implement task-001-auth.md.
        Work only in src/auth/.
        Reference contracts in .claude/contracts/.
        Do not modify files outside your scope."
```

### Isolation Strategies

**Git worktrees** (recommended): `git worktree add ../workspace-auth -b feature/auth`

**Directory boundaries**: Assign each agent to specific directories with explicit instructions.

**Branch-per-task**: Each agent on dedicated branch, merge at integration.

See `references/execution-patterns.md` for automation scripts.

## Phase 5: Integration

After parallel work completes:

1. Check contract compliance across all outputs
2. Identify integration gaps and create integration tests
3. Resolve conflicts and generate integration report

## Best Practices

- **Spend time on Phase 2**: Good decomposition is the multiplier
- **Contract-first**: Interfaces upfront prevent 80% of integration issues
- **Explicit boundaries**: Tell agents what they *cannot* touch
- **Small tasks**: Prefer more, smaller tasks over fewer, larger ones
- **CLAUDE.md conventions**: Ensure all agents follow identical patterns

## Anti-Patterns

- Tasks that share mutable state
- Circular dependencies between tasks
- Vague scope boundaries
- Missing contract definitions
- Skipping the integration phase

## Decomposition Prompt

Use the prompt in `references/decomposition-prompt.md` to decompose a PRD into parallel tasks.

## Quick Reference

### Starting Decomposition
```
Read the PRD in .claude/prd.md and decompose it following the parallel-agents skill.
Create architecture.md, contracts/, and task specs in tasks/.
```

### Launching Parallel Agents
```bash
# With git worktrees (recommended)
git worktree add ../workspace-auth -b feature/auth
cd ../workspace-auth
claude "Implement .claude/tasks/task-001-auth.md"
```

### Integration Check
```
Review all completed task outputs.
Verify contract compliance.
Create integration tests for component boundaries.
Report any gaps or conflicts.
```
