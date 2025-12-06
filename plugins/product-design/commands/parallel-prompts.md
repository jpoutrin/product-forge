---
description: Generate copy-paste prompts for launching parallel Claude Code agents
argument-hint: "[--wave <number>] [--format shell|markdown]"
---

# parallel-prompts

**Category**: Parallel Development

## Usage

```bash
/parallel-prompts [--wave <number>] [--format shell|markdown]
```

## Arguments

- `--wave`: Optional - Generate prompts for specific wave only (default: all waves)
- `--format`: Optional - Output format (default: markdown)
  - `shell`: Executable bash script with `claude` CLI commands
  - `markdown`: Copy-paste prompts in markdown format

## Purpose

Generate ready-to-use prompts for launching multiple Claude Code agents in parallel. Each prompt contains the task scope, contracts, boundaries, and acceptance criteria.

> "Beyond standalone usage, some of the most powerful applications involve running multiple Claude instances in parallel." — Claude Code Best Practices

## Prerequisites

- Run `/parallel-decompose <prd>` first
- Task specs must exist in `.claude/tasks/`
- `.claude/task-graph.md` must define waves

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Read Task Graph

Parse `.claude/task-graph.md` to understand wave structure and dependencies.

### 2. Read All Task Specs

For each task in `.claude/tasks/`:
- Parse metadata (wave, dependencies, scope)
- Extract file boundaries
- Get contract references
- Get acceptance criteria

### 3. Generate Prompts

Create `.claude/agent-prompts.md`:

```markdown
# Parallel Agent Execution Prompts

Generated: [date]
Source: [prd-file]
Total Tasks: [count]
Waves: [count]

---

## Wave 1 (No Dependencies)

Launch these agents in parallel:

### Task: task-001-users-app

**Worktree Setup** (run once per task):
```bash
git worktree add ../workspace-task-001 -b feature/task-001-users
cd ../workspace-task-001
```

**Agent Prompt** (copy this to Claude Code):
```
You are implementing task-001-users-app.

## Your Scope
CREATE/MODIFY these files only:
- apps/users/models.py
- apps/users/serializers.py
- apps/users/views.py
- apps/users/urls.py
- apps/users/tests/test_models.py
- apps/users/tests/test_views.py
- apps/users/tests/factories.py
- config/urls.py (add users URLs only)

## Boundary - DO NOT TOUCH
- apps/orders/* — owned by another task
- apps/products/* — owned by another task
- apps/*/migrations/* — defer to integration phase
- .claude/contracts/* — read-only reference

## Contracts (Read-Only)
Implement against these contracts exactly:
- .claude/contracts/types.py — UserDTO definition
- .claude/contracts/api-schema.yaml — /api/users/* endpoints

## Requirements
1. User model with email-based authentication
2. UserSerializer with explicit fields (no __all__)
3. UserViewSet with list, retrieve, create, update
4. Email uniqueness validation

## Conventions
Follow CLAUDE.md for:
- Code style and naming
- Error handling patterns
- Test patterns
- Logging format

## Acceptance Criteria
When complete, verify:
- [ ] User model matches UserDTO in contracts
- [ ] API endpoints match OpenAPI spec exactly
- [ ] Tests pass: pytest apps/users/
- [ ] Types pass: mypy apps/users/
- [ ] Lint passes: ruff check apps/users/
- [ ] No files modified outside scope
- [ ] No migrations created

## Completion
When done, commit your changes:
git add apps/users/ config/urls.py
git commit -m "feat(users): implement user management per task-001"
```

---

### Task: task-002-products-app

[Similar format...]

---

## Wave 2 (After Wave 1 Completes)

**Prerequisites**: Merge Wave 1 branches first:
```bash
git checkout main
git merge feature/task-001-users
git merge feature/task-002-products
git merge feature/task-003-shared
```

Then launch Wave 2 agents in parallel:

### Task: task-004-orders-app

[Similar format...]

---

## Wave 3 (After Wave 2 Completes)

[Similar format...]

---

## Integration Wave (Sequential)

After all parallel waves complete:

### Task: task-009-integration

```
You are performing integration after parallel development.

## Your Role
1. Merge all feature branches to main
2. Handle any migration conflicts
3. Run full test suite
4. Verify contract compliance
5. Generate integration report

## Steps
1. Run: python manage.py makemigrations --merge (if needed)
2. Run: python manage.py migrate
3. Run: pytest (full suite)
4. Run: mypy apps/
5. Verify all API endpoints match OpenAPI spec

## Output
Create .claude/integration-report.md with results.
```

---

## Execution Scripts

### Launch All Wave 1 Agents

```bash
#!/bin/bash
# launch-wave-1.sh

# Create worktrees
git worktree add ../workspace-task-001 -b feature/task-001-users
git worktree add ../workspace-task-002 -b feature/task-002-products
git worktree add ../workspace-task-003 -b feature/task-003-shared

# Launch agents in parallel (in separate terminals)
(cd ../workspace-task-001 && claude "$(cat .claude/prompts/task-001.txt)") &
(cd ../workspace-task-002 && claude "$(cat .claude/prompts/task-002.txt)") &
(cd ../workspace-task-003 && claude "$(cat .claude/prompts/task-003.txt)") &

wait
echo "Wave 1 complete"
```

### Monitor Progress

```bash
#!/bin/bash
# monitor.sh

while true; do
  clear
  echo "=== Parallel Agent Status ==="
  for ws in ../workspace-task-*; do
    task=$(basename $ws)
    branch=$(cd $ws && git branch --show-current)
    changes=$(cd $ws && git status --short | wc -l)
    echo "$task [$branch]: $changes files changed"
  done
  sleep 10
done
```

### Merge All Branches

```bash
#!/bin/bash
# merge-all.sh

git checkout main

for branch in feature/task-001 feature/task-002 feature/task-003; do
  echo "Merging $branch..."
  git merge $branch --no-edit || {
    echo "Conflict in $branch - resolve manually"
    exit 1
  }
done

echo "All branches merged"
```

### Cleanup Worktrees

```bash
#!/bin/bash
# cleanup.sh

for ws in ../workspace-task-*; do
  echo "Removing $ws..."
  git worktree remove $ws --force
done

echo "Worktrees cleaned up"
```
```

### 4. Create Individual Prompt Files (Optional)

If `--format shell`:

Create `.claude/prompts/` directory with individual files:
- `.claude/prompts/task-001.txt`
- `.claude/prompts/task-002.txt`
- etc.

### 5. Report Results

Output:
```
📋 Agent Prompts Generated

Output: .claude/agent-prompts.md

Wave Summary:
┌───────┬─────────┬────────────────────────────────────────┐
│ Wave  │ Tasks   │ Agents                                 │
├───────┼─────────┼────────────────────────────────────────┤
│ 1     │ 3       │ task-001, task-002, task-003           │
│ 2     │ 3       │ task-004, task-005, task-006           │
│ 3     │ 2       │ task-007, task-008                     │
│ 4     │ 1       │ task-009 (integration)                 │
└───────┴─────────┴────────────────────────────────────────┘

Execution:
1. Open 3 terminal windows
2. Copy Wave 1 worktree commands to each
3. Copy Wave 1 prompts to each Claude Code instance
4. Wait for all to complete
5. Merge branches, then repeat for Wave 2

Scripts generated:
✅ .claude/agent-prompts.md (all prompts)
✅ .claude/scripts/launch-wave-1.sh
✅ .claude/scripts/monitor.sh
✅ .claude/scripts/merge-all.sh
✅ .claude/scripts/cleanup.sh
```

## Example

```bash
# Generate all prompts
/parallel-prompts

# Generate only Wave 1
/parallel-prompts --wave 1

# Generate shell script format
/parallel-prompts --format shell

# View generated prompts
cat .claude/agent-prompts.md
```

## Prompt Structure

Each agent prompt includes:

1. **Scope**: Exactly which files to create/modify
2. **Boundary**: Files explicitly NOT to touch
3. **Contracts**: Read-only interface references
4. **Requirements**: What to implement
5. **Conventions**: Link to CLAUDE.md
6. **Acceptance**: Verification checklist

## Related Commands

- `/parallel-decompose` - Create tasks first
- `/parallel-integrate` - Run after all agents complete
