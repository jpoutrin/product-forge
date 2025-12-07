# Parallel Execution Patterns

All patterns assume artifacts are in `parallel/TS-XXXX-slug/`.

## Pattern 1: Git Worktrees (Recommended)

Each agent gets isolated working directory with shared git history.

### Setup Script

```bash
#!/bin/bash
# setup-worktrees.sh

PARALLEL_DIR="parallel/TS-0042-inventory-system"
TASKS_DIR="$PARALLEL_DIR/tasks"
WORKSPACE_ROOT="../workspaces"

mkdir -p "$WORKSPACE_ROOT"

for task_file in "$TASKS_DIR"/*.md; do
    task_name=$(basename "$task_file" .md)
    branch_name="feature/$task_name"

    echo "Creating worktree for $task_name..."
    git worktree add "$WORKSPACE_ROOT/$task_name" -b "$branch_name"
done

echo "Worktrees ready in $WORKSPACE_ROOT/"
```

### Parallel Execution Script

```bash
#!/bin/bash
# parallel-execute.sh

PARALLEL_DIR="parallel/TS-0042-inventory-system"
TASKS_DIR="$PARALLEL_DIR/tasks"
WORKSPACE_ROOT="../workspaces"
LOG_DIR="../logs"

mkdir -p "$LOG_DIR"

for task_file in "$TASKS_DIR"/*.md; do
    task_name=$(basename "$task_file" .md)
    workspace="$WORKSPACE_ROOT/$task_name"

    (
        cd "$workspace"
        echo "Starting agent for $task_name..."
        claude --dangerously-skip-permissions --print "$(cat $PARALLEL_DIR/prompts/$task_name.txt)" \
            > "$LOG_DIR/$task_name.log" 2>&1
        # Create completion marker
        touch .claude-task-complete
        echo "Completed $task_name"
    ) &
done

wait
echo "All agents complete. Logs in $LOG_DIR/"
```

> **Note**: The `.claude-task-complete` marker file signals task completion to orchestrators like `/parallel-run`.

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

PARALLEL_DIR="parallel/TS-0042-inventory-system"
TASKS_DIR="$PARALLEL_DIR/tasks"

for task_file in "$TASKS_DIR"/*.md; do
    task_name=$(basename "$task_file" .md)

    git checkout -b "feature/$task_name" main

    claude --dangerously-skip-permissions --print "$(cat $PARALLEL_DIR/prompts/$task_name.txt)"

    git add -A && git commit -m "feat: $task_name implementation"
    git checkout main
done
```

## Pattern 3: Directory Isolation

No git complexity, pure directory boundaries. Good for parallel execution.

```bash
#!/bin/bash
# directory-parallel.sh

PARALLEL_DIR="parallel/TS-0042-inventory-system"

# Define task-to-directory mapping
declare -A TASK_DIRS=(
    ["task-001-users"]="apps/users"
    ["task-002-products"]="apps/products"
    ["task-003-orders"]="apps/orders"
)

for task in "${!TASK_DIRS[@]}"; do
    dir="${TASK_DIRS[$task]}"

    (
        claude --dangerously-skip-permissions --print "Execute task from $PARALLEL_DIR/tasks/$task.md.
                       Read context from $PARALLEL_DIR/context.md first.
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

PARALLEL_DIR="parallel/TS-0042-inventory-system"
LOG_DIR="../logs"

while true; do
    clear
    echo "=== Agent Status for $PARALLEL_DIR ==="
    echo ""

    for task in $PARALLEL_DIR/tasks/task-*.md; do
        name=$(basename "$task" .md)
        # Check if corresponding branch has commits
        if git rev-parse --verify "feature/$name" >/dev/null 2>&1; then
            commits=$(git log --oneline "main..feature/$name" | wc -l | tr -d ' ')
            echo "✅ $name - $commits commits"
        else
            echo "⏳ $name - not started"
        fi
    done

    echo ""
    echo "Press Ctrl+C to exit"
    sleep 10
done
```

## Pattern 4: Claude Code SDK (Programmatic)

For advanced orchestration using the Claude Agent SDK:

```typescript
// orchestrator.ts
import { ClaudeAgent } from '@anthropic-ai/claude-agent-sdk';
import { readdir, readFile } from 'fs/promises';
import { join } from 'path';

async function runParallelTasks(parallelDir: string) {
  const tasksDir = join(parallelDir, 'tasks');
  const contextFile = join(parallelDir, 'context.md');

  const context = await readFile(contextFile, 'utf-8');
  const tasks = await readdir(tasksDir);

  const agents = tasks
    .filter(f => f.endsWith('.md'))
    .map(async (taskFile) => {
      const taskPath = join(tasksDir, taskFile);
      const taskContent = await readFile(taskPath, 'utf-8');

      const agent = new ClaudeAgent({
        systemPrompt: `You are implementing a task.
                       Context: ${context}
                       Follow contracts in ${parallelDir}/contracts/.`,
      });

      return agent.run(`Execute this task:\n\n${taskContent}`);
    });

  const results = await Promise.all(agents);
  return results;
}

// Usage
runParallelTasks('parallel/TS-0042-inventory-system');
```

## Choosing a Pattern

| Pattern | Best For | Complexity | Parallelism |
|---------|----------|------------|-------------|
| Git Worktrees | Full isolation, large teams | High | True parallel |
| Branch-Per-Task | Simple projects, solo dev | Low | Sequential |
| Directory Isolation | Clear component boundaries | Medium | True parallel |
| SDK Programmatic | Custom orchestration, CI/CD | High | True parallel |

## Completion Detection

All patterns should create a `.claude-task-complete` marker file upon task completion:

```bash
# At end of agent execution
touch .claude-task-complete
```

This enables:
- `/parallel-run` to detect task completion
- Monitoring scripts to report status
- Wave coordination (wait for all tasks before next wave)

## Tips for Success

1. **Start small**: Test with 2-3 parallel agents before scaling up
2. **Use /parallel-run**: Preferred method for automated orchestration
3. **Monitor progress**: Use the monitoring script to watch branches
4. **Handle failures**: Use `--retry-failed` flag to retry failed tasks
5. **Resource limits**: Don't overwhelm your machine - limit concurrent agents
6. **Contract verification**: Run `/parallel-integrate` after tasks complete
7. **Use prompts**: Reference `$PARALLEL_DIR/prompts/task-NNN.txt` for consistent agent instructions
