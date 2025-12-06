# Parallel Execution Patterns

## Pattern 1: Git Worktrees (Recommended)

Each agent gets isolated working directory with shared git history.

### Setup Script

```bash
#!/bin/bash
# setup-worktrees.sh

TASKS_DIR=".claude/tasks"
WORKSPACE_ROOT="../workspaces"

mkdir -p "$WORKSPACE_ROOT"

for task_file in "$TASKS_DIR"/*.md; do
    task_name=$(basename "$task_file" .md)
    branch_name="feature/$task_name"

    echo "Creating worktree for $task_name..."
    git worktree add "$WORKSPACE_ROOT/$task_name" -b "$branch_name"

    # Copy contracts to each workspace
    cp -r .claude/contracts "$WORKSPACE_ROOT/$task_name/.claude/"
done

echo "Worktrees ready in $WORKSPACE_ROOT/"
```

### Parallel Execution Script

```bash
#!/bin/bash
# parallel-execute.sh

TASKS_DIR=".claude/tasks"
WORKSPACE_ROOT="../workspaces"
LOG_DIR="../logs"

mkdir -p "$LOG_DIR"

for task_file in "$TASKS_DIR"/*.md; do
    task_name=$(basename "$task_file" .md)
    workspace="$WORKSPACE_ROOT/$task_name"

    (
        cd "$workspace"
        echo "Starting agent for $task_name..."
        claude --print "Read .claude/tasks/$task_name.md and implement it.
                       Follow contracts in .claude/contracts/.
                       Follow conventions in CLAUDE.md.
                       Stay within your assigned scope." \
            > "$LOG_DIR/$task_name.log" 2>&1
        echo "Completed $task_name"
    ) &
done

wait
echo "All agents complete. Logs in $LOG_DIR/"
```

### Cleanup Script

```bash
#!/bin/bash
# cleanup-worktrees.sh

WORKSPACE_ROOT="../workspaces"

for workspace in "$WORKSPACE_ROOT"/*; do
    if [ -d "$workspace" ]; then
        git worktree remove "$workspace" --force
    fi
done
```

## Pattern 2: Branch-Per-Task

Simpler setup, agents work sequentially but on different branches.

```bash
#!/bin/bash
# branch-execute.sh

TASKS_DIR=".claude/tasks"

for task_file in "$TASKS_DIR"/*.md; do
    task_name=$(basename "$task_file" .md)

    git checkout -b "feature/$task_name" main

    claude --print "Implement $task_file following .claude/contracts/"

    git add -A && git commit -m "feat: $task_name implementation"
    git checkout main
done
```

## Pattern 3: Directory Isolation

No git complexity, pure directory boundaries. Good for parallel execution.

```bash
#!/bin/bash
# directory-parallel.sh

# Define task-to-directory mapping
declare -A TASK_DIRS=(
    ["task-001-auth"]="src/auth"
    ["task-002-api"]="src/api"
    ["task-003-ui"]="src/components"
)

for task in "${!TASK_DIRS[@]}"; do
    dir="${TASK_DIRS[$task]}"

    (
        claude --print "Implement .claude/tasks/$task.md.
                       Work ONLY in $dir/.
                       Do NOT touch any other directories."
    ) &
done

wait
```

## Integration Merge Script

```bash
#!/bin/bash
# merge-all.sh

WORKSPACE_ROOT="../workspaces"

git checkout main

for workspace in "$WORKSPACE_ROOT"/*; do
    if [ -d "$workspace" ]; then
        branch=$(basename "$workspace")
        echo "Merging feature/$branch..."
        git merge "feature/$branch" --no-edit || {
            echo "Conflict in $branch - manual resolution needed"
            exit 1
        }
    fi
done

echo "All branches merged successfully"
```

## Monitoring Progress

```bash
#!/bin/bash
# monitor.sh

LOG_DIR="../logs"

while true; do
    clear
    echo "=== Agent Status ==="
    for log in "$LOG_DIR"/*.log; do
        task=$(basename "$log" .log)
        lines=$(wc -l < "$log")
        last=$(tail -1 "$log")
        echo "$task: $lines lines | $last"
    done
    sleep 5
done
```

## Pattern 4: Claude Code SDK (Programmatic)

For advanced orchestration using the Claude Agent SDK:

```typescript
// orchestrator.ts
import { ClaudeAgent } from '@anthropic-ai/claude-agent-sdk';
import { readdir, readFile } from 'fs/promises';
import { join } from 'path';

async function runParallelTasks() {
  const tasksDir = '.claude/tasks';
  const tasks = await readdir(tasksDir);

  const agents = tasks.map(async (taskFile) => {
    const taskPath = join(tasksDir, taskFile);
    const taskContent = await readFile(taskPath, 'utf-8');

    const agent = new ClaudeAgent({
      systemPrompt: `You are implementing: ${taskFile}
                     Follow contracts in .claude/contracts/.
                     Follow conventions in CLAUDE.md.`,
    });

    return agent.run(`Implement this task:\n\n${taskContent}`);
  });

  const results = await Promise.all(agents);
  return results;
}
```

## Choosing a Pattern

| Pattern | Best For | Complexity | Parallelism |
|---------|----------|------------|-------------|
| Git Worktrees | Full isolation, large teams | High | True parallel |
| Branch-Per-Task | Simple projects, solo dev | Low | Sequential |
| Directory Isolation | Clear component boundaries | Medium | True parallel |
| SDK Programmatic | Custom orchestration, CI/CD | High | True parallel |

## Tips for Success

1. **Start small**: Test with 2-3 parallel agents before scaling up
2. **Monitor logs**: Use the monitoring script to watch progress
3. **Handle failures**: Add retry logic for transient failures
4. **Resource limits**: Don't overwhelm your machine - limit concurrent agents
5. **Contract verification**: Run contract compliance checks after each task
