---
description: Verify integration after parallel agent execution and generate report
argument-hint: "[--tech django|typescript|go]"
---

# parallel-integrate

**Category**: Parallel Development

## Usage

```bash
/parallel-integrate [--tech django|typescript|go]
```

## Arguments

- `--tech`: Optional - Technology stack for specific checks (default: auto-detect)

## Purpose

Verify integration after all parallel agents complete their work. Checks contract compliance, boundary violations, runs tests, and generates an integration report.

## Prerequisites

- All parallel tasks completed
- All feature branches merged to main (or ready to merge)
- Run after `/parallel-prompts` execution

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Verify Branch Status

Check all task branches are complete:
```bash
# List task branches
git branch -a | grep feature/task-

# Check for unmerged branches
git branch --no-merged main | grep feature/task-
```

### 2. Merge Remaining Branches

If unmerged branches exist:
```bash
git checkout main
for branch in $(git branch --no-merged main | grep feature/task-); do
    echo "Merging $branch..."
    git merge $branch --no-edit
done
```

### 3. Technology-Specific Integration

#### For Django Projects

**Migration Merge**:
```bash
# Check for migration conflicts
python manage.py showmigrations | grep "\[ \]"

# If conflicts, merge migrations
python manage.py makemigrations --merge

# Apply all migrations
python manage.py migrate
```

**Verification**:
```bash
# Django system check
python manage.py check

# Run all tests
pytest

# Type checking
mypy apps/

# Linting
ruff check .
```

#### For TypeScript Projects

**Build Verification**:
```bash
# Type check
npx tsc --noEmit

# Lint
npm run lint

# Run tests
npm test

# Build
npm run build
```

#### For Go Projects

```bash
# Build and vet
go build ./...
go vet ./...

# Run tests
go test ./...

# Check formatting
gofmt -d .
```

### 4. Contract Compliance Check

For each task in `.claude/tasks/`:

**API Contract Check**:
- Compare implemented endpoints against `.claude/contracts/api-schema.yaml`
- Verify request/response schemas match
- Check error formats

**Type Contract Check**:
- Verify types match `.claude/contracts/types.py` (or `.ts`)
- Check for missing fields
- Verify enum values

### 5. Boundary Violation Check

For each task, verify:
- Files modified are within declared scope
- No files touched that were in "DO NOT TOUCH" list
- No unauthorized contract modifications

```bash
# Check git history for boundary violations
for task in $(ls .claude/tasks/); do
    echo "Checking $task boundaries..."
    # Compare committed files against task scope
done
```

### 6. Generate Integration Report

Create `.claude/integration-report.md`:

```markdown
# Integration Report

Generated: [date]
Source PRD: [prd-file]
Tasks Integrated: [count]

## Summary

| Check | Status | Details |
|-------|--------|---------|
| Branch Merge | ✅/❌ | X branches merged |
| Contract Compliance | ✅/⚠️/❌ | X/Y endpoints match |
| Boundary Violations | ✅/❌ | X violations found |
| Tests | ✅/❌ | X passed, Y failed |
| Type Check | ✅/❌ | X errors |
| Lint | ✅/❌ | X warnings |

## Contract Compliance

### API Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| GET /api/users/ | ✅ | Matches spec |
| POST /api/users/ | ⚠️ | Missing validation field |
| GET /api/orders/ | ✅ | Matches spec |

### Type Definitions

| Type | Status | Notes |
|------|--------|-------|
| UserDTO | ✅ | Matches contract |
| OrderDTO | ⚠️ | Extra field `updated_at` |

## Boundary Violations

| Task | File | Issue |
|------|------|-------|
| task-003 | apps/users/models.py | Modified (owned by task-001) |

## Test Results

```
pytest results:
  Passed: 142
  Failed: 2
  Skipped: 5
  Coverage: 84%

Failed tests:
  - test_order_creation_requires_user
  - test_notification_sends_email
```

## Migration Status (Django)

```
Migrations applied:
  users: 0001_initial, 0002_add_email_verified
  orders: 0001_initial
  products: 0001_initial

Merge migrations: None needed
```

## Action Items

### Must Fix (Blocking)
1. ❌ Fix failing test: test_order_creation_requires_user
2. ❌ Resolve boundary violation: task-003 modified users/models.py

### Should Fix (Non-Blocking)
1. ⚠️ Add missing validation field to POST /api/users/
2. ⚠️ Remove extra field from OrderDTO or update contract

### Recommended
1. 💡 Increase test coverage from 84% to 90%
2. 💡 Add integration tests for cross-app workflows

## Next Steps

[If all checks pass]:
1. ✅ Integration complete
2. Create PR for review
3. Deploy to staging

[If issues found]:
1. Fix blocking issues listed above
2. Re-run /parallel-integrate
3. Verify all checks pass
```

### 7. Report Results

Output to console:
```
🔄 Integration Verification Complete

┌────────────────────┬────────┬─────────────────────────┐
│ Check              │ Status │ Details                 │
├────────────────────┼────────┼─────────────────────────┤
│ Branch Merge       │ ✅     │ 9 branches merged       │
│ Contract Compliance│ ⚠️     │ 18/20 endpoints match   │
│ Boundary Violations│ ❌     │ 1 violation found       │
│ Tests              │ ❌     │ 142 passed, 2 failed    │
│ Type Check         │ ✅     │ 0 errors                │
│ Lint               │ ✅     │ 0 warnings              │
└────────────────────┴────────┴─────────────────────────┘

📄 Full report: .claude/integration-report.md

[If issues]:
⚠️  Issues found - review report and fix before proceeding

Action items:
1. Fix boundary violation in task-003
2. Fix 2 failing tests
3. Update contract for missing validation field

[If clean]:
✅ Integration successful!

Next steps:
1. Review .claude/integration-report.md
2. Create pull request
3. Deploy to staging
```

## Example

```bash
# Run integration check
/parallel-integrate

# Specify Django
/parallel-integrate --tech django

# After fixing issues, re-run
/parallel-integrate

# View report
cat .claude/integration-report.md
```

## Integration Checklist

- [ ] All feature branches merged
- [ ] No merge conflicts
- [ ] Migrations applied (Django)
- [ ] All tests pass
- [ ] Type checks pass
- [ ] Lint passes
- [ ] No boundary violations
- [ ] Contract compliance verified
- [ ] Integration report generated

## Related Commands

- `/parallel-decompose` - Create tasks
- `/parallel-prompts` - Generate agent prompts
- `/parallel-ready-[tech]` - Re-assess if needed
