---
description: Orchestrate parallel agent execution with git worktrees
argument-hint: <parallel-dir> [--generate-only] [--wave N] [--dry-run] [--max-concurrent N] [--retry-failed]
---

# parallel-run

**Category**: Parallel Development

## Usage

```bash
/parallel-run <parallel-dir> [options]
```

## Arguments

- `<parallel-dir>`: Required - Path to decomposed parallel folder (e.g., `parallel/TS-0042-inventory/`)
- `--generate-only`: Only generate script, don't execute (for manual runs)
- `--dry-run`: Preview execution plan without changes
- `--wave N`: Run only wave N (default: run all waves sequentially)
- `--max-concurrent N`: Limit concurrent agents (default: 3)
- `--retry-failed`: Retry previously failed tasks
- `--skip <task-ids>`: Skip specific task(s), comma-separated

## Purpose

Execute parallel agent development tasks using Git Worktrees. This command:
1. Validates the parallel directory and manifest.json
2. Generates `scripts/run-parallel.sh` orchestrator
3. **By default**: Executes and monitors progress within Claude session
4. Updates manifest.json with execution status

## Prerequisites

- Run `/parallel-decompose` first (creates tasks, prompts, manifest.json)
- Git working tree is clean (no uncommitted changes)
- Current branch is main/master (base branch for worktrees)
- Claude Code CLI available: `claude --version`

---

## Execution Instructions for Claude Code

When this command is run, Claude Code should follow these steps:

### 0. Parse Arguments

Extract from user input:
- `PARALLEL_DIR`: The parallel directory path
- `GENERATE_ONLY`: Boolean, true if `--generate-only` specified
- `DRY_RUN`: Boolean, true if `--dry-run` specified
- `WAVE`: Integer or null, specific wave if `--wave N` specified
- `MAX_CONCURRENT`: Integer, default 3
- `RETRY_FAILED`: Boolean, true if `--retry-failed` specified
- `SKIP_TASKS`: List of task IDs to skip

### 1. Validate Parallel Directory

```bash
# Check manifest.json exists
ls "$PARALLEL_DIR/manifest.json"

# Check prompts directory exists
ls "$PARALLEL_DIR/prompts/"

# Check tasks directory exists
ls "$PARALLEL_DIR/tasks/"
```

If any check fails, display error:
```
ERROR: Invalid parallel directory '$PARALLEL_DIR'
Missing: manifest.json | prompts/ | tasks/

Run '/parallel-decompose' first to create task specifications.
```

### 2. Read Manifest and Build Execution Plan

Read `$PARALLEL_DIR/manifest.json` to extract:
- Task list from `tasks.files`
- Technology stack from `technology`
- Source PRD and Tech Spec paths

Read each task file to build wave structure:
- Parse YAML frontmatter for `wave`, `deps`, `id`, `component`
- Group tasks by wave number
- Identify dependencies between waves

### 3. Pre-Flight Checks

```bash
# Check git status is clean
git status --porcelain

# Get current branch
git rev-parse --abbrev-ref HEAD

# Check Claude CLI is available
which claude

# List existing worktrees (check for conflicts)
git worktree list
```

Display warnings for:
- Uncommitted changes: "WARNING: Uncommitted changes detected. Consider committing or stashing."
- Existing worktrees that match task names: "WARNING: Worktree '../workspaces/task-001' already exists."

### 4. Display Execution Plan

For `--dry-run` or before execution, display:

```
=== Parallel Execution Plan ===

Parallel Dir: parallel/TS-0042-inventory-system
Tech Spec: TS-0042
Base Branch: main
Max Concurrent: 3

Wave 1 (3 tasks, parallel):
  - task-001-users      -> ../workspaces/task-001 (feature/task-001-users)
  - task-002-products   -> ../workspaces/task-002 (feature/task-002-products)
  - task-003-shared     -> ../workspaces/task-003 (feature/task-003-shared)

Wave 2 (2 tasks, parallel):
  - task-004-orders     -> ../workspaces/task-004 (feature/task-004-orders)
  - task-005-api        -> ../workspaces/task-005 (feature/task-005-api)

Total Tasks: 5
Estimated Worktree Space: ~750MB (5 worktrees x ~150MB)
```

If `--dry-run`, stop here with message: "Dry run complete. No files modified."

### 5. Generate Orchestration Script

Create `$PARALLEL_DIR/scripts/run-parallel.sh` using the template.

The script should:
1. Accept `MAX_CONCURRENT` as environment variable
2. Create worktrees for each wave before launching
3. Launch agents in parallel (respecting MAX_CONCURRENT)
4. Wait for wave completion before starting next wave
5. Detect completion via `.claude-task-complete` marker
6. Output progress in parseable format for Claude monitoring
7. Log agent output to `$PARALLEL_DIR/logs/`

**Progress output format** (for Claude to parse):
```
[PROGRESS] wave=1 task=task-001 status=started
[PROGRESS] wave=1 task=task-001 status=completed commits=5
[PROGRESS] wave=1 task=task-002 status=failed error=timeout
[PROGRESS] wave=1 status=completed tasks=3/3
[PROGRESS] wave=2 status=started
```

Create `$PARALLEL_DIR/scripts/monitor-live.sh` for manual monitoring.

### 6. Update Manifest with Execution Config

Update `$PARALLEL_DIR/manifest.json` to add `execution` block:

```json
{
  "execution": {
    "status": "pending",
    "script_path": "scripts/run-parallel.sh",
    "workspace_root": "../workspaces",
    "options": {
      "max_concurrent": 3
    },
    "waves": [
      {
        "wave": 1,
        "status": "pending",
        "tasks": ["task-001", "task-002", "task-003"]
      },
      {
        "wave": 2,
        "status": "pending",
        "tasks": ["task-004", "task-005"]
      }
    ],
    "failed_tasks": [],
    "skipped_tasks": []
  }
}
```

### 7. Execute and Monitor (Default Behavior)

If `--generate-only` is NOT specified:

1. **Start the orchestrator script**:
   ```
   Use Bash tool with:
   - command: "cd $PROJECT_ROOT && ./$PARALLEL_DIR/scripts/run-parallel.sh"
   - run_in_background: true
   ```

2. **Monitor progress** by polling BashOutput every 30 seconds:
   ```
   Use BashOutput tool with:
   - bash_id: [id from step 1]
   - block: false
   ```

3. **Parse output** for `[PROGRESS]` lines and report to user:
   ```
   Wave 1 Progress:
     task-001-users: COMPLETED (5 commits)
     task-002-products: RUNNING...
     task-003-shared: COMPLETED (3 commits)

   Overall: 2/3 tasks complete in Wave 1
   ```

4. **Detect completion** when output contains:
   ```
   [PROGRESS] execution status=completed
   ```
   Or failure:
   ```
   [PROGRESS] execution status=failed
   ```

5. **Final report**:
   ```
   === Parallel Execution Complete ===

   Wave 1: 3/3 tasks completed
   Wave 2: 2/2 tasks completed
   Total: 5/5 tasks completed

   Branches created:
     - feature/task-001-users (5 commits)
     - feature/task-002-products (3 commits)
     - feature/task-003-shared (4 commits)
     - feature/task-004-orders (6 commits)
     - feature/task-005-api (8 commits)

   Next step: /parallel-integrate --parallel-dir $PARALLEL_DIR
   ```

### 8. Handle --generate-only Mode

If `--generate-only` is specified, skip step 7 and display:

```
=== Scripts Generated ===

Created:
  - $PARALLEL_DIR/scripts/run-parallel.sh (orchestrator)
  - $PARALLEL_DIR/scripts/monitor-live.sh (live dashboard)
  - $PARALLEL_DIR/logs/ (for agent output)

To execute manually:
  1. Open a new terminal
  2. cd to project root
  3. Run: ./$PARALLEL_DIR/scripts/run-parallel.sh

To monitor (in another terminal):
  ./$PARALLEL_DIR/scripts/monitor-live.sh

Override concurrency:
  MAX_CONCURRENT=5 ./$PARALLEL_DIR/scripts/run-parallel.sh

After completion:
  /parallel-integrate --parallel-dir $PARALLEL_DIR
```

### 9. Handle --retry-failed Mode

If `--retry-failed` is specified:

1. Read manifest.json `execution.failed_tasks`
2. Only create worktrees for failed tasks
3. Re-run those tasks
4. Update manifest on completion

```
=== Retrying Failed Tasks ===

Failed tasks from previous run:
  - task-003-shared (error: timeout)

Creating worktree for retry...
Launching agent...
```

### 10. Handle --wave N Mode

If `--wave N` is specified:

1. Check that wave N-1 dependencies are satisfied (branches exist)
2. Only execute tasks in wave N
3. Display dependency check results

```
=== Running Wave 2 Only ===

Checking Wave 1 dependencies...
  feature/task-001-users: EXISTS
  feature/task-002-products: EXISTS
  feature/task-003-shared: EXISTS

All dependencies satisfied. Proceeding with Wave 2.
```

---

## Error Handling

### Pre-execution Errors

```
ERROR: Uncommitted changes in working directory
  Run 'git stash' or commit changes before parallel execution.

ERROR: Worktree already exists: ../workspaces/task-001
  Run 'git worktree remove ../workspaces/task-001' or use --force.

ERROR: Branch already exists: feature/task-001-users
  Previous execution was interrupted. Use '--retry-failed' to continue.

ERROR: manifest.json not found in '$PARALLEL_DIR'
  Run '/parallel-decompose' first to create task specifications.

ERROR: Claude CLI not found
  Install Claude Code CLI: https://claude.ai/code
```

### Runtime Errors

The orchestrator script handles:
1. Agent process failure (non-zero exit) -> marks task as failed
2. Timeout (configurable, default 2 hours per task) -> marks task as failed
3. Missing completion marker after process exit -> marks task as failed
4. Git conflicts during worktree creation -> aborts with message

Failed tasks are logged in manifest.json for `--retry-failed`.

---

## Examples

```bash
# Default: Execute and monitor all waves
/parallel-run parallel/TS-0042-inventory/

# Preview what would happen
/parallel-run parallel/TS-0042-inventory/ --dry-run

# Generate scripts only, run manually later
/parallel-run parallel/TS-0042-inventory/ --generate-only

# Run only wave 1
/parallel-run parallel/TS-0042-inventory/ --wave 1

# Limit to 2 concurrent agents
/parallel-run parallel/TS-0042-inventory/ --max-concurrent 2

# Retry failed tasks from previous run
/parallel-run parallel/TS-0042-inventory/ --retry-failed

# Skip problematic tasks
/parallel-run parallel/TS-0042-inventory/ --skip task-003,task-005
```

---

## Related Commands

- `/parallel-setup` - One-time project initialization
- `/parallel-decompose` - Create tasks and prompts (run before this)
- `/parallel-integrate` - Verify integration (run after this)
