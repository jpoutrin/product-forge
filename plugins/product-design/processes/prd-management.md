# PRD Management System

**Comprehensive process for organizing, tracking, and managing Product Requirements Documents**

Version: 1.0.0

---

## 🎯 Overview

This process defines how to systematically manage PRDs throughout their lifecycle, from creation through implementation to archival. It ensures proper organization, status tracking, and clear visibility of all product documentation.

---

## 📁 Directory Structure

### Standard PRD Organization

```
product-docs/
├── prds/
│   ├── active/           # Currently being implemented
│   │   ├── product-prds/ # Full product PRDs
│   │   └── feature-prds/ # Feature-specific PRDs
│   ├── review/           # Under review/approval
│   ├── approved/         # Approved, awaiting implementation
│   └── archive/          # Completed/deprecated
│       ├── 2025/
│       └── 2024/
├── personas/             # User personas
├── positioning/          # Product positioning docs
├── discovery/            # Discovery phase docs
└── tasks/               # Generated task lists
```

### File Naming Conventions

1. **Full Product PRDs**: `<product-name>-prd.md`
   - Example: `inventory-system-prd.md`

2. **Feature PRDs**: `<feature-name>-frd.md`
   - Example: `user-authentication-frd.md`

3. **Simple Feature PRDs**: `<feature-name>-simple-frd.md`
   - Example: `quick-search-simple-frd.md`

4. **Task Lists**: `<prd-name>-tasks.md`
   - Example: `inventory-system-prd-tasks.md`

---

## 📊 PRD Status Lifecycle

### Status Definitions

1. **DRAFT** - Initial creation, work in progress
2. **REVIEW** - Ready for stakeholder review
3. **APPROVED** - Signed off, ready for implementation
4. **ACTIVE** - Currently being implemented
5. **COMPLETE** - Implementation finished
6. **ARCHIVED** - No longer relevant/superseded

### Status Metadata Format

All PRDs must include this header:

```yaml
---
status: DRAFT
version: 1.0
created: 2025-01-06
last_updated: 2025-01-06
author: John Doe
approved_by: 
approved_date: 
task_file: ./tasks/feature-name-frd-tasks.md
---
```

### Status Transition Rules

```
DRAFT → REVIEW → APPROVED → ACTIVE → COMPLETE → ARCHIVED
         ↓                      ↓
      ARCHIVED              ARCHIVED
```

- PRDs can be archived from REVIEW or ACTIVE if cancelled
- Status changes must include a comment explaining the reason
- Each status change updates the `last_updated` field

---

## 🔗 PRD-to-Task Linking

### Link Structure

In the PRD, add to the "Implementation Tracking" section:

```markdown
## Implementation Tracking

Task List: ./tasks/feature-x-frd-tasks.md
Generated: 2025-01-06
Status: See task file for current progress
```

### Task File Reference

In the generated task file header:

```markdown
# Feature X Implementation Tasks

Source PRD: ../prds/active/feature-prds/feature-x-frd.md
Generated: 2025-01-06
Total Tasks: 15
Completed: 0

## Tasks
- [ ] 1.0 Setup and Configuration
  - [ ] 1.1 Review framework documentation
  - [ ] 1.2 Configure development environment
...
```

---

## 🔍 PRD Discovery

### Search Strategies

1. **By Status**: Group PRDs by their current lifecycle status
2. **By Type**: Separate product, feature, and simple feature PRDs
3. **By Date**: Sort by creation, update, or approval date
4. **By Content**: Full-text search across all PRDs
5. **By Author**: Find all PRDs by a specific author

### Metadata Extraction

Extract and index these fields for searching:
- Title (from H1 header)
- Status
- Version
- Dates (created, updated, approved)
- Author
- Product/Feature name
- Linked task file

---

## 📈 Progress Tracking

### Implementation Progress Calculation

```python
def calculate_progress(task_file_path):
    total_tasks = count_all_tasks(task_file_path)
    completed_tasks = count_completed_tasks(task_file_path)
    progress_percentage = (completed_tasks / total_tasks) * 100
    return {
        "total": total_tasks,
        "completed": completed_tasks,
        "percentage": progress_percentage
    }
```

### Progress Reporting Format

```markdown
## PRD Implementation Progress

**Feature Authentication System**
- Status: ACTIVE
- Progress: 67% (10/15 tasks complete)
- Started: 2025-01-05
- Est. Completion: 2025-01-10

### Completed Milestones
- ✅ Database schema setup
- ✅ Basic authentication flow
- 🔄 User management interface (in progress)
- ⏳ Testing and documentation (pending)
```

---

## 🗂️ Archival Process

### When to Archive

Archive PRDs when:
1. Implementation is 100% complete
2. PRD is superseded by a newer version
3. Project/feature is cancelled
4. PRD is over 1 year old and inactive

### Archive Structure

```
archive/
├── 2025/
│   ├── Q1/
│   │   ├── completed/
│   │   │   └── feature-x-frd-v2.0-COMPLETE.md
│   │   └── cancelled/
│   │       └── feature-y-frd-v1.0-CANCELLED.md
```

### Archive Metadata

Add to PRD header before archiving:

```yaml
archive_date: 2025-01-06
archive_reason: Implementation complete
final_task_completion: 100%
implementation_duration: 15 days
```

---

## 🛠️ Command Implementations

### list-prds

Lists all PRDs with their current status and location:
- Scans all PRD directories
- Extracts metadata from headers
- Shows status, version, and progress
- Groups by status or type

### organize-prds

Moves PRDs to their proper directory based on status:
- Reads PRD metadata
- Determines correct location
- Moves file preserving git history
- Updates any references

### prd-status

Updates PRD status and moves to appropriate directory:
- Validates new status
- Updates metadata
- Moves file if needed
- Logs status change with comment

### find-prd

Searches PRDs by various criteria:
- Content search using grep
- Metadata filtering
- Returns ranked results
- Shows preview snippets

### prd-report

Generates comprehensive PRD summary:
- Status distribution
- Progress metrics
- Timeline visualization
- Bottleneck identification

### prd-check

Validates PRD format and completeness:
- Checks required metadata
- Validates section structure
- Verifies file references
- Reports missing elements

### prd-progress

Shows implementation progress from linked tasks:
- Reads linked task file
- Calculates completion percentage
- Shows task breakdown
- Estimates completion date

### prd-archive

Moves completed/cancelled PRDs to archive:
- Adds archive metadata
- Creates archive directory structure
- Preserves file history
- Updates references

---

## ✅ Best Practices

1. **Always Update Metadata** - Keep PRD headers current
2. **Link Tasks Immediately** - Create task reference when generating tasks
3. **Regular Status Reviews** - Update PRD status weekly
4. **Archive Promptly** - Don't let old PRDs clutter active directories
5. **Use Consistent Naming** - Follow file naming conventions strictly
6. **Document Changes** - Add comments for all status changes
7. **Validate Before Moving** - Check PRD format before status changes
8. **Maintain References** - Update links when moving files

---

## 🚨 Common Issues and Solutions

### Issue: Lost PRD Files
**Solution**: Use `find-prd` to locate, then `organize-prds` to restore structure

### Issue: Broken Task Links
**Solution**: Use relative paths and update when moving PRDs

### Issue: Unclear Progress
**Solution**: Ensure task files use proper checkbox format

### Issue: Status Mismatch
**Solution**: Run `prd-check` to validate and fix metadata

---

*This PRD management system ensures systematic tracking of all product documentation throughout the development lifecycle.*