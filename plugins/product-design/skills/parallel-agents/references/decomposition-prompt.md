# PRD Decomposition Prompt

Use this prompt to decompose a PRD into parallel tasks:

---

Read the PRD in `.claude/prd.md` and perform the following:

## 1. Architecture Analysis

Create `.claude/architecture.md` with:
- System overview and component diagram (ASCII or Mermaid)
- Data flow between components
- Technology choices and rationale
- Component boundaries and ownership

## 2. Contract Definition

Create contracts in `.claude/contracts/`:

**types.ts** - Shared TypeScript types:
- Domain entities
- API request/response types
- Shared enums and constants

**api-schema.yaml** - OpenAPI specification:
- All endpoints with full schemas
- Error response formats
- Authentication requirements

## 3. Task Decomposition

Create task specs in `.claude/tasks/`:

For each logical component, create a task file following the template in `references/task-template.md`.

Requirements:
- Each task should be completable in 2-4 hours
- Tasks should touch separate files/directories
- Identify and document all dependencies between tasks
- Flag any tasks that MUST be sequential

## 4. Dependency Analysis

At the end of architecture.md, include:
- Task dependency graph (ASCII diagram)
- Recommended execution order
- Parallelization opportunities
- Integration checkpoints

## 5. CLAUDE.md Conventions

Create/update CLAUDE.md with project conventions:
- Code style and formatting rules
- Error handling patterns
- Logging conventions
- Test file organization
- Naming conventions

---

## Expected Output Summary

After decomposition, provide:
- Total tasks created
- Maximum parallelization (how many can run simultaneously)
- Critical path (longest sequential chain)
- Estimated total effort

---

## Example Decomposition

Given a PRD for a "User Management System", the output might be:

### Tasks Created
1. `task-001-contracts.md` - Define shared types and API schema
2. `task-002-auth.md` - Authentication service (login, logout, JWT)
3. `task-003-users-api.md` - User CRUD endpoints
4. `task-004-users-ui.md` - User management UI components
5. `task-005-db.md` - Database schema and migrations
6. `task-006-integration.md` - Integration tests and final assembly

### Dependency Graph
```
task-001 (contracts) --+--> task-002 (auth)     --+
                       +--> task-003 (users-api) -+--> task-006 (integration)
                       +--> task-004 (users-ui)  --+
task-005 (db) ---------------------------------->--+
```

### Summary
- **Total tasks**: 6
- **Max parallelization**: 4 (tasks 2, 3, 4, 5 can run simultaneously after task-001)
- **Critical path**: task-001 -> task-003 -> task-006 (3 sequential steps)
- **Estimated effort**: 12-18 hours total, 6-8 hours with parallelization
