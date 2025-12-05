# Focused Task Management

**LLM-optimized workflow for maintaining deep focus on single tasks**

Version: 1.0.0

---

## <¯ Overview

Focused task management is a methodology designed specifically for LLM-assisted development. It enforces single-task focus, automatic state synchronization, and seamless context resumption across sessions.

---

## >à Core Philosophy

### The One-Task Rule

**Only ONE task file can be in focus at any time.**

Benefits:
- Eliminates context switching overhead
- Maintains deep understanding of current work
- Prevents scattered attention
- Simplifies state management

### Automatic Synchronization

**Every action updates both TodoTools and the task file.**

Benefits:
- No manual sync needed
- State persists across sessions
- Progress visible in real-time
- Git-trackable history

---

## = Focus Workflow

### 1. Starting Focus

```bash
task-focus tasks/active/TASK-001-auth.md
```

What happens:
1. **Enforce One-Task Rule**: Check focus/ is empty
2. **Move to Focus**: Transfer file to focus/ directory
3. **Load State**: Parse tasks into TodoTools
4. **Start Tracking**: Begin time and progress tracking
5. **Show Context**: Display current progress and next task

### 2. During Focus

#### Working on Tasks
```bash
# Complete current subtask
task-done

# Complete with notes
task-done --note "Used JWT instead of sessions"

# Skip a subtask
task-skip --reason "Not needed after design change"

# Block on dependency
task-block --reason "Waiting for API endpoint"
```

#### Automatic Updates
- Each `task-done` updates the file immediately
- Progress recalculates automatically
- Work log appends continuously
- Time tracking accumulates

#### State Visibility
```bash
# Check current progress
task-status

# See all subtasks
TodoRead

# Review work log
task-log
```

### 3. Context Switching

#### Planned Pause
```bash
task-pause --reason "Switching to urgent bugfix"
```

What happens:
1. Final sync of all changes
2. Add pause note to work log
3. Move to paused/ directory
4. Clear TodoTools state

#### Emergency Switch
```bash
task-focus tasks/active/URGENT-TASK.md --force
```

Automatically:
1. Saves current state
2. Moves current to paused/
3. Loads new task

### 4. Resuming Work

```bash
# Resume from paused
task-resume TASK-001

# Or refocus directly
task-focus tasks/paused/TASK-001-auth.md
```

Restores:
- All task states
- Progress position
- Work context
- Time tracking

### 5. Completing Tasks

```bash
task-complete
```

Actions:
1. Verify all subtasks done
2. Calculate final metrics
3. Add completion note
4. Move to completed/
5. Clear focus

---

## =Ý Task File Evolution

### Initial State
```markdown
---
task_id: TASK-001
title: Implement User Authentication
status: pending
priority: high
created: 2025-01-06
estimated_hours: 8
---

# TASK-001: Implement User Authentication

## Tasks

- [ ] 1.0 Setup and Research
  - [ ] 1.1 Review auth documentation
  - [ ] 1.2 Set up environment
```

### After Focus Session
```markdown
---
task_id: TASK-001
title: Implement User Authentication  
status: in_progress
priority: high
created: 2025-01-06
last_updated: 2025-01-06 16:45
estimated_hours: 8
actual_hours: 3.5
---

# TASK-001: Implement User Authentication

## Progress
Overall: 40% (4/10 subtasks)

## Tasks

- [x] 1.0 Setup and Research [COMPLETED 14:35]
  - [x] 1.1 Review auth documentation (0.5h)
  - [x] 1.2 Set up environment (0.5h)
  
- [-] 2.0 Implementation [IN PROGRESS]
  - [x] 2.1 Create user model (1.5h)
  - [x] 2.2 Add auth endpoints (1h)
  - [-] 2.3 JWT implementation
  
## Work Log

### 2025-01-06 14:30-16:45 (2.25h)
- Started focus session
- Completed all setup tasks
- Implemented basic user model with email/password
- Created login/logout endpoints
- Started JWT implementation
- **Decision**: Using PyJWT for token handling
- **Blocker**: Need to clarify refresh token strategy
- Paused for urgent bugfix
```

---

## =à Focus Commands

### Primary Commands

| Command | Description | Example |
|---------|-------------|---------|
| `task-focus` | Start focusing on a task | `task-focus auth-task.md` |
| `task-done` | Complete current subtask | `task-done --note "Fixed edge case"` |
| `task-pause` | Pause with reason | `task-pause --reason "Team meeting"` |
| `task-resume` | Resume paused task | `task-resume TASK-001` |
| `task-complete` | Mark entire task complete | `task-complete` |

### Status Commands

| Command | Description | Example |
|---------|-------------|---------|
| `task-status` | Show current focus status | `task-status` |
| `task-log` | View work log | `task-log --last 5` |
| `task-next` | Show next subtask | `task-next` |
| `task-sync` | Force synchronization | `task-sync` |

### Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `task-block` | Block with reason | `task-block --reason "API not ready"` |
| `task-unblock` | Remove block | `task-unblock` |
| `task-skip` | Skip subtask | `task-skip --reason "Deprecated"` |
| `task-add` | Add new subtask | `task-add "2.4 Add rate limiting"` |

---

## = Session Continuity

### End of Session

Automatic session summary:
```markdown
## Session Summary - 2025-01-06 16:45

**Task**: TASK-001 User Authentication
**Duration**: 2.25 hours
**Progress**: 20% ’ 40% (+20%)

**Completed**:
-  All setup tasks
-  User model implementation
-  Basic auth endpoints

**In Progress**:
- = JWT implementation (50% done)

**Next**: Complete JWT refresh token logic

**To Resume**:
```bash
task-focus tasks/paused/TASK-001-auth.md
```
```

### Session Handoff

Perfect for LLM context switches:
1. Clear task state preserved
2. Decisions documented in work log
3. Exact resumption point marked
4. No context reconstruction needed

---

## ¡ Advanced Features

### Time Boxing

```bash
# Focus for specific duration
task-focus auth-task.md --duration 2h

# Get reminder at 90%
task-focus auth-task.md --remind 1.5h
```

### Deep Work Mode

```bash
# Minimal interruptions
task-focus --deep

# Disables:
# - Progress notifications
# - Time reminders  
# - Auto-sync (sync on complete only)
```

### Task Templates

```bash
# Create from template
task-new --template feature --name "Payment Integration"

# Templates available:
# - feature: Full feature implementation
# - bugfix: Bug investigation and fix
# - research: Technical research task
# - refactor: Code refactoring task
```

---

## =Ê Metrics and Insights

### Focus Analytics

```bash
task-analytics --period week

Focus Time: 24.5 hours
Tasks Completed: 12
Average Task Duration: 2.04 hours
Focus Sessions: 8
Context Switches: 3
```

### Productivity Patterns

```bash
task-patterns

Most Productive: 14:00-17:00 (65% completion rate)
Longest Focus: 3.5 hours (TASK-003)
Common Blockers: External dependencies (40%)
```

---

##  Best Practices

### DO:
-  Complete subtasks atomically
-  Document decisions in work log
-  Use pause reasons for context
-  Review task before focusing
-  Update estimates based on actuals
-  One subtask at a time

### DON'T:
- L Work on multiple tasks
- L Skip work log updates
- L Leave focus without status update
- L Batch task completions
- L Ignore blockers

---

## =¨ Troubleshooting

### Lost Focus State

```bash
# Recover from unexpected exit
task-recover

# Finds most recent focus
# Restores TodoTools state
# Shows last position
```

### Sync Issues

```bash
# Validate and repair
task-validate --fix
task-sync --force
```

### Multiple Focus Files

```bash
# Clean up (moves extras to active)
task-cleanup-focus
```

---

*Focused task management ensures deep, productive work with perfect state management across LLM sessions.*