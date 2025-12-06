# PRD Decomposition Prompt

Use this prompt to decompose a PRD into parallel tasks:

---

Read the PRD in `.claude/prd.md` and perform the following:

## 0. Tech Spec Analysis (if provided)

If a Tech Spec (TS-XXXX) is provided:

1. **Read and validate Tech Spec**:
   - Verify status is APPROVED or REFERENCE
   - Warn if DRAFT (not ready for decomposition)

2. **Extract from Tech Spec**:
   - **Design Overview** → Use for `.claude/architecture.md`
   - **Data Model** → Use for `.claude/contracts/types.py` or `types.ts`
   - **API Specification** → Use for `.claude/contracts/api-schema.yaml`
   - **Component boundaries** → Use for task ownership
   - **RFC link** (if any) → Include in task metadata

3. **Record linkage**:
   - Add `tech_spec_ref: TS-XXXX` to each generated task
   - Add `rfc_ref: RFC-XXXX` if Tech Spec links to an RFC
   - Add Tech Spec path to `.claude/architecture.md`

4. **Skip redundant steps**:
   - If Tech Spec has complete Data Model, skip generating types
   - If Tech Spec has complete API Spec, skip generating api-schema.yaml
   - Focus on task decomposition and boundaries

**If no Tech Spec provided**: Generate contracts from PRD and display warning:
> "Consider creating a Tech Spec first for better contract definitions"

---

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
- Source PRD file
- Source Tech Spec file (if provided)
- Source RFC file (if linked via Tech Spec)
- Total tasks created
- Maximum parallelization (how many can run simultaneously)
- Critical path (longest sequential chain)
- Estimated total effort

---

## Example Decomposition

Given a PRD for a "User Management System" with Tech Spec TS-0042, the output might be:

### Source Documents
- **PRD**: `docs/user-management-prd.md`
- **Tech Spec**: `tech-specs/approved/TS-0042-user-management.md`
- **RFC**: `rfcs/approved/RFC-0018-auth-strategy.md` (linked from Tech Spec)

### Tasks Created
1. `task-001-contracts.md` - Define shared types and API schema (from Tech Spec)
2. `task-002-auth.md` - Authentication service (login, logout, JWT)
3. `task-003-users-api.md` - User CRUD endpoints
4. `task-004-users-ui.md` - User management UI components
5. `task-005-db.md` - Database schema and migrations
6. `task-006-integration.md` - Integration tests and final assembly

Each task includes:
- `tech_spec_ref: TS-0042`
- `rfc_ref: RFC-0018` (if linked)

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
