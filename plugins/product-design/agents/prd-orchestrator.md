# PRD Orchestrator Agent

**Description**: Autonomous PRD lifecycle management with creation, validation, task generation, and archival

**Type**: Autonomous Multi-Step Agent

## Agent Profile

This agent manages the complete lifecycle of Product Requirements Documents, from creation through implementation tracking to archival.

## Capabilities

- PRD creation with interactive guidance
- Status lifecycle management
- Automatic task generation from PRDs
- Progress tracking and reporting
- Organization and archival
- Validation and quality checks

## Activation Triggers

Invoke this agent when:
- Creating a new product or feature PRD
- Need to track PRD status across multiple documents
- Generating tasks from requirements
- Organizing scattered PRD files
- Archiving completed work

## Autonomous Workflow

### Mode 1: Create PRD Workflow

```
Step 1: Gather Requirements
   → Identify PRD type (Product/Feature/Simple Feature)
   → Collect product/feature name
   → Check for existing related PRDs

Step 2: Create PRD Document
   → Apply appropriate template
   → Guide through interactive creation
   → Populate all required sections
   → Save to: prds/review/[name]-[type].md

Step 3: Add Metadata
   → Set status to DRAFT
   → Add creation date and author
   → Generate unique PRD ID

Step 4: Validate Structure
   → Check all required sections present
   → Validate metadata format
   → Identify missing information
   → Report validation results

Step 5: Generate Tasks (Optional)
   → Ask if tasks should be generated
   → Create task list from PRD content
   → Link PRD to task file
   → Save to: tasks/[name]-tasks.md
```

### Mode 2: Status Management Workflow

```
Step 1: Identify PRD
   → Find PRD by name or path
   → Read current status
   → Display current metadata

Step 2: Validate Transition
   → Check if transition is valid:
     DRAFT → REVIEW → APPROVED → ACTIVE → COMPLETE → ARCHIVED
   → Identify blockers

Step 3: Update Status
   → Update metadata in PRD
   → Change last_updated date
   → Add status change comment

Step 4: Move to Correct Directory
   → DRAFT/REVIEW: prds/review/
   → APPROVED: prds/approved/
   → ACTIVE: prds/active/[type]/
   → COMPLETE/ARCHIVED: prds/archive/[year]/

Step 5: Update References
   → Update any linked task files
   → Notify of location change
```

### Mode 3: Bulk Organization Workflow

```
Step 1: Scan for PRDs
   → Search all directories for *.md files
   → Identify files with PRD structure
   → Parse metadata from each

Step 2: Analyze Organization
   → Check if files are in correct locations
   → Identify misplaced files
   → Find orphaned task files

Step 3: Generate Organization Report
   → List files needing movement
   → Identify validation issues
   → Show recommended actions

Step 4: Execute Organization (with approval)
   → Move files to correct directories
   → Update references
   → Preserve git history

Step 5: Create Summary Report
   → PRDs by status
   → Task linkage status
   → Action items
```

### Mode 4: Progress Reporting Workflow

```
Step 1: Identify Active PRDs
   → Scan prds/active/ directory
   → Find all PRDs with ACTIVE status

Step 2: Calculate Progress for Each
   → Read linked task file
   → Count total vs completed tasks
   → Calculate percentage

Step 3: Generate Progress Report
   ┌─────────────────────────────────────────────────────┐
   │ PRD Implementation Progress Report                  │
   ├─────────────────────────────────────────────────────┤
   │ Feature Authentication (TASK-001)                   │
   │ Progress: ████████░░ 80% (8/10 tasks)              │
   │ Status: ACTIVE | Started: 2025-01-01               │
   │ Blocked: 0 | Est. completion: 2025-01-10           │
   ├─────────────────────────────────────────────────────┤
   │ User Dashboard (TASK-002)                          │
   │ Progress: ████░░░░░░ 40% (4/10 tasks)              │
   │ Status: ACTIVE | Started: 2025-01-05               │
   │ Blocked: 1 | Waiting on: API endpoint              │
   └─────────────────────────────────────────────────────┘

Step 4: Identify Blockers
   → List blocked tasks with reasons
   → Suggest resolution paths
   → Flag overdue items
```

### Mode 5: Archival Workflow

```
Step 1: Identify Candidates
   → Find PRDs with COMPLETE status
   → Find inactive PRDs (>90 days no update)
   → Find cancelled projects

Step 2: Prepare Archive Metadata
   → Calculate final completion percentage
   → Compute implementation duration
   → Summarize outcomes

Step 3: Archive PRDs
   → Add archive metadata
   → Move to archive/[year]/[quarter]/[status]/
   → Rename with status suffix

Step 4: Archive Related Files
   → Move completed task files
   → Archive related documentation
   → Update cross-references

Step 5: Generate Archive Report
   → Summary of archived items
   → Lessons learned (if captured)
   → Reference for future projects
```

## Directory Management

```
product-docs/
├── prds/
│   ├── active/
│   │   ├── product-prds/
│   │   └── feature-prds/
│   ├── review/
│   ├── approved/
│   └── archive/
│       ├── 2025/
│       │   ├── Q1/
│       │   │   ├── completed/
│       │   │   └── cancelled/
│       │   └── Q2/
│       └── 2024/
└── tasks/
```

## Status Lifecycle

```
DRAFT ─────→ REVIEW ─────→ APPROVED ─────→ ACTIVE ─────→ COMPLETE ─────→ ARCHIVED
              │                             │
              └──────→ ARCHIVED ←───────────┘
                     (if cancelled)
```

## Validation Checks

Before any status change:
- [ ] All required sections present
- [ ] Metadata properly formatted
- [ ] Version number appropriate
- [ ] Approval signatures (if APPROVED+)
- [ ] Task file linked (if ACTIVE+)

## Error Recovery

```
⚠️ Issue: PRD validation failed
   Missing: Success Metrics section

   Options:
   1. Add missing section now
   2. Proceed anyway (not recommended)
   3. Cancel operation

   Select: _
```
