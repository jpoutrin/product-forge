# Task Specification Template

Use this template for each task in `.claude/tasks/`.

```markdown
# Task: [Descriptive Name]

## Metadata
- **ID**: task-XXX
- **Priority**: P0/P1/P2
- **Estimated effort**: 1-4 hours
- **Dependencies**: [task-IDs or "None"]
- **Tech Spec**: TS-XXXX (if decomposed from Tech Spec)
- **RFC**: RFC-XXXX (if linked via Tech Spec)
- **Wave**: [wave number for parallel execution]

## Scope

### Files to Create/Modify
- `src/module/file.ts` - [purpose]
- `src/module/file.test.ts` - [purpose]

### Files to NOT Touch
- `src/other/*` - owned by task-XXX
- `shared/config.ts` - shared resource

## Inputs

### Contracts
- `.claude/contracts/types.ts` - Domain types
- `.claude/contracts/api-schema.yaml` - API spec

### Dependencies
- task-001 must complete first (provides X)

## Requirements

### Functional
1. [Specific requirement]
2. [Specific requirement]

### Non-Functional
- Performance: [constraint]
- Security: [constraint]

## Acceptance Criteria
- [ ] All endpoints match OpenAPI spec
- [ ] Unit test coverage >80%
- [ ] No lint errors
- [ ] Follows project conventions in CLAUDE.md

## Notes
[Any additional context, edge cases, or decisions]
```

## Task Naming Convention

```
task-{number}-{component}-{feature}.md

Examples:
- task-001-auth-login.md
- task-002-api-users.md
- task-003-ui-dashboard.md
- task-004-db-migrations.md
```

## Dependency Graph

For complex projects, include a dependency visualization:

```
task-001 (contracts) --+--> task-002 (auth)
                       +--> task-003 (api) ----> task-006 (integration)
                       +--> task-004 (ui)  ----> task-006 (integration)
task-005 (db) -----------------------------> task-006 (integration)
```

## Parallelization Score

Rate each task's parallelization potential:

| Score | Criteria |
|-------|----------|
| **High** | No dependencies, isolated directory, clear contract |
| **Medium** | Some shared types, minimal coordination needed |
| **Low** | Sequential dependency, shared state, requires coordination |

## Example Task

```markdown
# Task: User Authentication Service

## Metadata
- **ID**: task-002-auth
- **Priority**: P0
- **Estimated effort**: 3 hours
- **Dependencies**: task-001-contracts

## Scope

### Files to Create/Modify
- `src/auth/auth.service.ts` - Core authentication logic
- `src/auth/auth.controller.ts` - HTTP endpoints
- `src/auth/auth.middleware.ts` - JWT validation middleware
- `src/auth/auth.service.test.ts` - Unit tests

### Files to NOT Touch
- `src/api/*` - owned by task-003-api
- `src/db/*` - owned by task-005-db

## Inputs

### Contracts
- `.claude/contracts/types.ts` - User, Session, Token types
- `.claude/contracts/api-schema.yaml` - /auth/* endpoints

## Requirements

### Functional
1. POST /auth/login - Validate credentials, return JWT
2. POST /auth/logout - Invalidate session
3. GET /auth/me - Return current user from token

### Non-Functional
- Tokens expire after 24 hours
- Passwords never logged or returned in responses

## Acceptance Criteria
- [ ] All /auth/* endpoints match OpenAPI spec
- [ ] JWT tokens validated correctly
- [ ] Unit test coverage >80%
- [ ] No secrets in logs
```
