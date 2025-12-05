# Task List Management

**Guidelines for implementing and tracking task lists in projects**

Version: 1.0.0

---

## 🎯 Overview

This process provides guidelines for systematically implementing and tracking tasks from a structured task list. It ensures consistent task execution, proper tracking, and clear communication throughout the implementation process.

---

## 📋 Prerequisites

**Before starting task implementation:**
1. **Task List File** - A properly formatted task list (generated from PRD or manually created)
2. **Project Setup** - Development environment ready
3. **Clear Requirements** - Understanding of what each task entails

---

## 🔄 Task Implementation Workflow

### 1. Initial Setup
- Read the task list file completely before starting any implementation
- Use TodoWrite to initialize tracking for all tasks in the list
- Identify dependencies between tasks
- Verify all required resources are available
- **MANDATORY: Confirm first sub-task is documentation review for all coding tasks**

### 2. Sequential Execution
- Work through tasks in numerical order (1.0, 1.1, 1.2, 2.0, etc.)
- **ENFORCE: First sub-task MUST be documentation review - NO EXCEPTIONS**
- Complete all sub-tasks before moving to the next parent task
- Only mark one task as "in_progress" at a time
- Respect task dependencies and prerequisites

### 3. One Sub-task at a Time
- Focus on a single sub-task until completion
- **CRITICAL: For documentation review tasks, share key findings before proceeding**
- Do NOT start the next sub-task until user confirmation with "yes" or "y"
- Provide clear status update after each sub-task completion
- Document any discoveries or changes needed

### 4. Completion Protocol
**CRITICAL: These steps are MANDATORY and must be executed immediately upon task completion**

When a sub-task is finished, immediately:
1. Update TodoWrite status to "completed"
2. **MECHANICALLY UPDATE** markdown `[ ]` to `[x]` in the task list file using Edit/MultiEdit
3. Update relevant files section if new files were created/modified
4. **DO NOT PROCEED** to next task until file update is complete

When all sub-tasks of a parent task are completed:
1. Mark the parent task as completed in TodoWrite
2. **MECHANICALLY UPDATE** parent task from `[ ]` to `[x]` in markdown
3. Provide summary of what was accomplished
4. Verify all updates are saved before moving on

**Remember: No task is complete until the file is updated!**

---

## 🔧 Tool Integration

### 1. TodoWrite/TodoRead Integration

Use the following format for task tracking:

```python
todos = [
    {
        "id": "1.0",
        "content": "Parent Task: Implement Authentication",
        "status": "pending",  # pending, in_progress, completed
        "priority": "high"    # high, medium, low
    },
    {
        "id": "1.1",
        "content": "Create user login form",
        "status": "pending", 
        "priority": "medium"
    }
]
```

**Best Practices:**
- Update status after each task completion
- Use TodoRead to verify current status before starting new tasks
- Keep task descriptions concise but informative
- Maintain consistent priority levels

### 2. Markdown File Updates

**CRITICAL: Mechanical updates are MANDATORY after each task completion**

Directly update the markdown task list file after each task completion:

```markdown
- [x] 1.0 Implement Authentication
  - [x] 1.1 Create user login form
  - [x] 1.2 Implement validation logic
  - [ ] 1.3 Add session management
- [ ] 2.0 Create User Dashboard
  - [ ] 2.1 Design dashboard layout
  - [ ] 2.2 Implement user data fetching
```

**Update Rules:**
- **MANDATORY**: Change `[ ]` to `[x]` IMMEDIATELY upon task completion
- **NO EXCEPTIONS**: Every completed task must be mechanically updated in the file
- Use Edit or MultiEdit tool to update task status - do not wait or batch updates
- Never mark parent task complete until all sub-tasks are done
- Add notes about significant changes or discoveries
- **Workflow**: Complete task → Update file → Report completion → Move to next task

---

## 📁 File Tracking

### 1. Relevant Files Section

Maintain an up-to-date list of all files created or modified:

```markdown
## Relevant Files

### Created Files
- `auth/login.py` - Handles user authentication and session management
- `components/LoginForm.js` - React component for the user login interface
- `tests/auth/test_login.py` - Unit tests for authentication functions

### Modified Files
- `config/settings.py` - Added authentication configuration
- `routes/index.js` - Added authentication routes
```

### 2. File Update Protocol
- Add new files to the list immediately after creation
- Update descriptions if a file's purpose changes
- Group files by functionality for better organization
- Include file paths relative to project root

---

## 💬 Progress Communication

### 1. Standard Update Format

**Starting a documentation review task (MANDATORY FIRST STEP):**
```
📚 Starting task 1.1: Review Django authentication documentation
- Reviewing Django auth system best practices
- Checking for recommended patterns and security considerations
```

**Starting an implementation task:**
```
🚀 Starting task 1.2: Create user login form
- Will implement using Django forms as per documentation
- Following security patterns from Django docs
```

**During implementation:**
```
📝 Implementation update:
- Created LoginForm.js component
- Added basic validation rules
- Integrated with existing auth context
```

**Completion:**
```
✅ Completed task 1.1: Create user login form
- File created: components/LoginForm.js
- All tests passing
- Ready for next task

📋 Next task is 1.2: Implement validation logic
Proceed? (y/n)
```

### 2. Concise Reporting Guidelines
- Keep status updates brief and focused
- Report any issues or obstacles encountered
- Highlight deviations from original task description
- Include relevant code snippets only when necessary
- Mention test results when applicable

---

## 🚨 Error Handling

When encountering issues:

1. **Document the Problem:**
   ```
   ⚠️ Issue encountered in task 1.2:
   - Validation library conflict with existing dependencies
   - Proposed solution: Use built-in validation instead
   - Estimated impact: +30 minutes
   ```

2. **Seek Approval for Changes:**
   - Explain the issue clearly
   - Propose solution with rationale
   - Wait for user approval before proceeding

3. **Update Task List:**
   - Add notes about the issue and resolution
   - Update time estimates if significantly affected

---

## 🎯 Quality Assurance

Before marking any task complete:

1. **Documentation Compliance:**
   - [ ] **VERIFIED: Documentation was reviewed BEFORE implementation**
   - [ ] Implementation follows documented best practices
   - [ ] API/framework patterns are correctly applied

2. **Code Quality Checks:**
   - [ ] Code follows project conventions
   - [ ] No linting errors
   - [ ] Proper error handling implemented
   - [ ] Comments added where necessary

3. **Testing:**
   - [ ] Unit tests written and passing
   - [ ] Manual testing completed
   - [ ] Edge cases considered
   - [ ] Integration verified

4. **Documentation:**
   - [ ] Code comments updated
   - [ ] README updated if needed
   - [ ] API documentation current
   - [ ] Relevant files list updated

---

## ⚠️ API Documentation Review Enforcement

### MANDATORY Protocol
**NO CODING WITHOUT DOCUMENTATION REVIEW**

1. **Before ANY implementation begins:**
   - The FIRST sub-task MUST be completed
   - Documentation findings MUST be shared
   - Best practices MUST be identified
   - Anti-patterns MUST be noted

2. **Documentation Review Output:**
   ```
   📚 Documentation Review Summary:
   - Framework: Django 4.2
   - Key patterns: Class-based views, model forms
   - Security considerations: CSRF, SQL injection prevention
   - Best practices: Use get_object_or_404(), proper permissions
   - Avoid: Direct SQL queries, storing passwords in plain text
   ```

3. **Enforcement:**
   - If documentation review is missing, STOP and add it
   - If attempting to skip documentation, REFUSE to proceed
   - Always reference documentation findings in implementation

---

## 📊 Progress Tracking

### Daily Summary Format
```markdown
## Progress Summary - [Date]

### Completed Tasks
- [x] 1.1 Create user login form
- [x] 1.2 Implement validation logic

### In Progress
- [ ] 1.3 Add session management (50% complete)

### Blockers
- Waiting for API endpoint specification for task 2.1

### Files Modified Today
- components/LoginForm.js
- utils/validation.js
- tests/auth/test_validation.py
```

---

## 🔄 Task Discovery Protocol

When new tasks are discovered during implementation:

1. **Add to Task List:**
   ```markdown
   - [ ] 1.4 [NEW] Implement rate limiting for login attempts
   ```

2. **Update TodoWrite:**
   ```python
   {
       "id": "1.4",
       "content": "[NEW] Implement rate limiting for login attempts",
       "status": "pending",
       "priority": "medium"
   }
   ```

3. **Notify User:**
   ```
   📌 New task discovered:
   - Task 1.4: Implement rate limiting for login attempts
   - Reason: Security best practice not in original PRD
   - Priority: Medium
   - Should we add this to the current sprint? (y/n)
   ```

---

## ✅ Final Checklist

When working with task lists, always:

1. ✅ **ENFORCE: Documentation review MUST be completed FIRST for all coding tasks**
2. ✅ Use both TodoWrite/TodoRead tools AND update markdown files
3. ✅ Never proceed to the next task without explicit user approval
4. ✅ Follow the exact sequence of tasks as defined in the list
5. ✅ Keep "Relevant Files" section continuously updated
6. ✅ Report completion status clearly after each task
7. ✅ Handle newly discovered tasks by adding them to both tracking systems
8. ✅ Test/verify each implementation before marking as complete
9. ✅ Maintain clear communication throughout the process
10. ✅ Document any deviations or discoveries
11. ✅ Ensure code quality standards are met

---

## 🚀 Quick Commands Reference

```bash
# Common commands during task implementation
npm test                 # Run tests after implementation
npm run lint            # Check code quality
git add .              # Stage changes
git commit -m "..."    # Commit with descriptive message
git status             # Verify changes
```

---

*This task management process ensures systematic, trackable, and high-quality implementation of all project tasks. Following these guidelines leads to better collaboration and more predictable delivery.*