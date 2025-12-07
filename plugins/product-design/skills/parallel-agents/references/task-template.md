# Task Specification Template

Use this compact YAML format for each task in `parallel/TS-XXXX-slug/tasks/`.

## Compact Task Format (Token-Efficient)

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
- Email uniqueness validation

## Checklist
- [ ] Model matches UserDTO in contracts/types.py
- [ ] API matches /api/users/* in contracts/api-schema.yaml
- [ ] pytest apps/users/ passes
- [ ] mypy apps/users/ passes
- [ ] ruff check apps/users/ passes
- [ ] No files modified outside scope
```

## YAML Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Task identifier (task-NNN) |
| `component` | Yes | System component name |
| `wave` | Yes | Dependency wave number |
| `deps` | Yes | Task IDs this depends on (empty list if none) |
| `blocks` | No | Task IDs this blocks |
| `agent` | Yes | Recommended agent type |
| `tech_spec` | No | Tech Spec ID (if applicable) |
| `contracts` | Yes | Contract files to reference (relative paths) |

## Scope Section Format

Use compact notation:
- `CREATE:` - Files to create (use glob patterns)
- `MODIFY:` - Existing files to modify
- `BOUNDARY:` - Files NOT to touch (owned by other tasks)

## Task Naming Convention

```
task-{number}-{component}.md

Examples:
- task-001-users.md
- task-002-products.md
- task-003-orders.md
- task-004-api.md
```

## Agent Type Selection

| Task Files | Agent | Description |
|------------|-------|-------------|
| `apps/*/models.py`, `apps/*/views.py` | `django-expert` | Django models, views, serializers |
| `api/*.py`, `routers/*.py` | `fastapi-expert` | FastAPI endpoints |
| `src/components/*.tsx` | `react-typescript-expert` | React components |
| `**/test_*.py`, `**/tests/*.py` | `python-testing-expert` | Python tests |
| `*.spec.ts`, `*.test.tsx` | `playwright-testing-expert` | TypeScript/E2E tests |
| `terraform/`, `docker-compose.yml` | `devops-expert` | Infrastructure |

## Contract References

Contracts are in the same parallel directory:
```
parallel/TS-0042-slug/
├── contracts/
│   ├── types.py        # Reference as: contracts/types.py
│   └── api-schema.yaml # Reference as: contracts/api-schema.yaml
└── tasks/
    └── task-001-users.md
```

## Complete Example

```yaml
---
id: task-002
component: orders
wave: 2
deps: [task-001]
blocks: [task-005]
agent: django-expert
tech_spec: TS-0042
contracts: [contracts/types.py, contracts/api-schema.yaml]
---
# task-002: Order Processing

## Scope
CREATE: apps/orders/{models,views,serializers,urls}.py, apps/orders/tests/*.py
MODIFY: config/urls.py
BOUNDARY: apps/users/*, apps/products/*, apps/*/migrations/*

## Requirements
- Order model with user foreign key
- OrderSerializer with nested user info
- OrderViewSet (list, retrieve, create)
- Status transitions (pending → confirmed → shipped)

## Checklist
- [ ] Model matches OrderDTO in contracts/types.py
- [ ] API matches /api/orders/* in contracts/api-schema.yaml
- [ ] Foreign key to User uses contracts definition
- [ ] Status enum matches contracts/types.py OrderStatus
- [ ] pytest apps/orders/ passes
- [ ] mypy apps/orders/ passes
- [ ] No files modified outside scope
```

## Why Compact Format?

1. **Token efficiency**: Less tokens for agent context
2. **Faster parsing**: YAML frontmatter is standard
3. **Clear boundaries**: Scope section is scannable
4. **Actionable checklist**: Verification is explicit
