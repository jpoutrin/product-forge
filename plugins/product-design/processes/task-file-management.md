# Task File Management System

**Comprehensive process for managing task files with LLM-optimized workflow**

Version: 1.0.0

---

## 🎯 Overview

This system provides a dual-tracking approach for task management, optimized for LLM sessions. It combines in-memory TodoTools with persistent markdown files, ensuring tasks persist across sessions while maintaining quick updates during active work.

---

## 🏗️ System Architecture

### Dual Tracking System

1. **TodoRead/TodoWrite Tools** (Session memory)
   - Fast, in-memory task tracking
   - Immediate updates during work
   - Session-specific state

2. **Markdown Task Files** (Persistent storage)
   - Permanent record across sessions
   - Rich metadata and context
   - Git-trackable history

### Automatic Synchronization

```
TodoWrite Update → Trigger Sync → Update Markdown File
Markdown Edit → Detect Change → Update TodoTools
```

---

## 📁 Directory Structure

```
tasks/
├── focus/           # Current WIP (1 file max)
├── active/          # Ready to work on
├── paused/          # Context switched
├── completed/       # Recently finished
└── archive/         # Long-term storage
    ├── 2025/
    └── 2024/
```

### Directory Rules

1. **focus/**: Only ONE task file at a time
2. **active/**: All approved, ready tasks
3. **paused/**: Include pause reason in file
4. **completed/**: Auto-archive after 30 days
5. **archive/**: Organized by year/quarter

---

## 📄 Task File Format

### Standard Header

```yaml
---
task_id: TASK-001
title: Implement User Authentication
status: in_progress
priority: high
created: 2025-01-06
last_updated: 2025-01-06
estimated_hours: 8
actual_hours: 3.5
assignee: @ai-assistant
blocked: false
blocked_reason: 
dependencies: [TASK-002, TASK-003]
prd_source: ../product-docs/prds/active/auth-frd.md
---
```

### Task Structure

```markdown
# TASK-001: Implement User Authentication

## Overview
Brief description of the task and its goals.

## Context
- PRD: [Authentication Feature](../product-docs/prds/active/auth-frd.md)
- Related Tasks: TASK-002, TASK-003
- Sprint: 2025-W02

## Progress
Overall: 40% (4/10 subtasks)

## Tasks

### 1.0 Setup and Research [COMPLETE]
- [x] 1.1 Review Django auth documentation (1h)
- [x] 1.2 Set up development environment (0.5h)

### 2.0 Implementation [IN PROGRESS]
- [x] 2.1 Create user model (2h)
- [x] 2.2 Add authentication views (2h)
- [ ] 2.3 Implement JWT tokens (est. 2h)
- [ ] 2.4 Add password reset flow (est. 3h)

### 3.0 Testing [PENDING]
- [ ] 3.1 Unit tests for auth functions (est. 2h)
- [ ] 3.2 Integration tests for API (est. 2h)
- [ ] 3.3 Security audit (est. 1h)

### 4.0 Documentation [PENDING]
- [ ] 4.1 API documentation (est. 1h)
- [ ] 4.2 User guide (est. 1h)

## Work Log

### 2025-01-06
- Started task, completed setup phase
- Implemented basic user model
- **Hours**: 3.5
- **Next**: Continue with JWT implementation

### 2025-01-05
- Task created from PRD
- Initial planning and estimation

## Blocked Items
None currently.

## Notes
- Using Django's built-in auth with custom extensions
- JWT for API authentication, sessions for web
```

---

## 🔄 Synchronization Process

### TodoTools → File Sync

When TodoWrite updates a task:

1. **Detect Change**: Monitor TodoWrite calls
2. **Find File**: Locate corresponding task file
3. **Update Status**: 
   - Map todo status to file checkboxes
   - Update header metadata
   - Add timestamp to work log
4. **Calculate Progress**: Update percentage
5. **Save File**: Atomic write to prevent corruption

### File → TodoTools Sync

When entering a new session:

1. **Scan Focus**: Check focus/ directory first
2. **Load State**: Parse task file metadata
3. **Initialize Todos**: Populate TodoWrite with current state
4. **Set Context**: Restore working context

### Sync Mapping

```python
# Status Mapping
TODO_STATUS = {
    "pending": "[ ]",
    "in_progress": "[-]",
    "completed": "[x]",
    "cancelled": "[~]"
}

# Priority Mapping  
PRIORITY_EMOJI = {
    "high": "🔴",
    "medium": "🟡", 
    "low": "🟢"
}
```

---

## 🎯 Focus Workflow

### Starting Focus

```bash
task-focus <task-file>
```

1. Ensure focus/ is empty (one task rule)
2. Move task file to focus/
3. Load into TodoTools
4. Display current progress
5. Show next subtask

### During Focus

- All updates sync automatically
- Work log appends continuously
- Time tracking accumulates
- Progress updates in real-time

### Ending Focus

```bash
task-unfocus [--pause|--complete]
```

1. Final sync of all changes
2. Update total hours worked
3. Move file to appropriate directory:
   - `--pause`: → paused/ (with reason)
   - `--complete`: → completed/
   - Default: → active/

---

## 📊 Progress Tracking

### Simple Calculation

```
Progress = (Completed Subtasks / Total Subtasks) × 100
```

### Progress Indicators

- Parent task complete only when all subtasks done
- Use `[-]` for in-progress (counts as 0.5)
- Exclude `[~]` cancelled tasks from totals

### Time Tracking

```markdown
## Work Sessions
- 2025-01-06 09:00-11:30: Setup and initial implementation (2.5h)
- 2025-01-06 14:00-15:30: Completed user model (1.5h)
Total: 4h (of 8h estimated)
```

---

## 🛠️ Task Management Commands

### Core Commands

1. **task-focus** - Move task to focus and start work
2. **task-unfocus** - End focus session
3. **task-sync** - Force sync between tools and files
4. **task-list** - List tasks by directory
5. **task-progress** - Show progress across all tasks
6. **task-validate** - Check task file format
7. **task-archive-completed** - Move old completed tasks

### Workflow Commands

1. **task-pause** - Pause with reason
2. **task-resume** - Resume from paused
3. **task-complete** - Mark as done and move
4. **task-block** - Mark as blocked with reason

---

## 🔍 Task Discovery

### Finding Tasks

```bash
task-find <search-term>              # Search all tasks
task-list --status in_progress       # List by status  
task-list --dir focus               # Show focused task
task-dependencies TASK-001          # Show dependencies
```

### Task Reports

```bash
task-report                         # Overall statistics
task-burndown --sprint 2025-W02    # Sprint progress
task-blocked                        # All blocked tasks
```

---

## ⚡ LLM Optimization

### Session Continuity

1. **Quick Context**: Focus dir = immediate context
2. **State Restore**: TodoTools populated from files
3. **Progress Visible**: See exactly where left off
4. **Work Log**: Historical context for decisions

### Context Switching

```bash
# Save current context
task-pause --reason "Switching to urgent bug fix"

# Start new work
task-focus urgent-bugfix-task.md

# Later, resume original
task-resume auth-task.md
```

### Session Handoff

End of session summary:
```markdown
## Session Summary - 2025-01-06

**Focused Task**: TASK-001 User Authentication
**Progress**: 40% → 60% (+20%)
**Hours Worked**: 3.5
**Completed**:
- User model implementation
- Basic auth views

**Next Steps**:
- Implement JWT tokens (2.3)
- Currently in: tasks/focus/

**To Resume**:
```bash
task-focus tasks/focus/TASK-001-auth.md
```
```

---

## ✅ Best Practices

### DO:
- ✅ Keep only ONE task in focus
- ✅ Update work log with decisions/context
- ✅ Use pause reason for context switches
- ✅ Track actual vs estimated hours
- ✅ Move completed tasks promptly
- ✅ Regular sync validation

### DON'T:
- ❌ Edit files while in TodoTools (causes conflicts)
- ❌ Keep multiple tasks in focus
- ❌ Skip work log updates
- ❌ Leave blocked tasks without reasons
- ❌ Forget to unfocus when switching

---

## 🚨 Error Recovery

### Sync Conflicts

If sync fails:
1. Run `task-validate <file>`
2. Check for syntax errors
3. Run `task-sync --force`
4. Review sync log

### Lost Focus

If session ends unexpectedly:
1. Check `tasks/focus/` directory
2. Run `task-recover`
3. Resume with `task-focus`

### Corrupted Files

1. Check `tasks/.backup/` for recent versions
2. Run `task-repair <file>`
3. Manually merge if needed

---

*This task file management system ensures seamless task tracking across LLM sessions with automatic synchronization and intelligent workflow management.*