---
description: Review and sync captured feedback to Product Forge
argument-hint: "[--status] [--review] [--export]"
---

# Sync Feedback

Review feedback captured from your Claude Code sessions and sync to Product Forge.

## Usage

```bash
/sync-feedback              # Interactive review mode (default)
/sync-feedback --status     # Show statistics only
/sync-feedback --review     # Review pending feedback
/sync-feedback --export     # Export to GitHub issues format
```

## Options

| Option | Description |
|--------|-------------|
| `--status` | Show feedback statistics across all projects |
| `--review` | Interactive review of pending feedback items |
| `--export` | Export reviewed feedback to GitHub issue format |

## Feedback Location

All feedback is stored in `~/.claude/learnings/`:

```
~/.claude/learnings/
├── projects.json          # Registry of opted-in projects
├── stats.json             # Global statistics
└── projects/
    └── {project-slug}/
        └── feedback/
            ├── improvement/
            ├── skill-idea/
            ├── command-idea/
            ├── bug-report/
            └── pattern/
```

## Workflow

```
1. Enable hooks → /enable-feedback-hooks
2. Work normally → Feedback captured at session end
3. Review       → /sync-feedback --review
4. Submit       → /sync-feedback --export → Create GitHub issue
```

## Execution Instructions

When the user runs this command:

### Status Mode (--status or default with no pending items)

1. **Read statistics** from `~/.claude/learnings/stats.json`

2. **Read projects** from `~/.claude/learnings/projects.json`

3. **Count pending items** by scanning `~/.claude/learnings/projects/*/feedback/**/*.md`

4. **Display summary**:
   ```
   Product Forge Feedback Status
   ==============================

   Total feedback captured: 15
   Pending review: 8

   By Type:
     improvement:  6 (4 pending)
     skill-idea:   4 (2 pending)
     command-idea: 2 (1 pending)
     bug-report:   2 (1 pending)
     pattern:      1 (0 pending)

   By Project:
     product-forge:  7 items
     my-django-app:  5 items
     frontend-app:   3 items

   Run /sync-feedback --review to review pending items.
   ```

### Review Mode (--review)

1. **Find all pending feedback** files:
   ```bash
   find ~/.claude/learnings/projects -name "*.md" -path "*/feedback/*"
   ```

2. **For each pending item**, display:
   ```
   [1/8] improvement - product-forge
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Title: Add status filtering to /task-list command

   Description:
   The /task-list command shows all tasks regardless of status.
   Adding --status flag would help filter to pending/completed items.

   Target: plugins/product-design/commands/task-list.md

   Actions:
     [a] Approve - Mark as reviewed, ready for sync
     [d] Dismiss - Remove this feedback
     [s] Skip    - Review later
     [e] Edit    - Open in editor
     [q] Quit    - Exit review

   Select action:
   ```

3. **Process user action**:
   - **Approve**: Update status in frontmatter to `reviewed`
   - **Dismiss**: Move to `~/.claude/learnings/synced/dismissed/`
   - **Skip**: Continue to next item
   - **Edit**: Allow inline editing of the feedback
   - **Quit**: Exit review mode

4. **Show summary** at end:
   ```
   Review complete:
     Approved: 5
     Dismissed: 2
     Skipped: 1

   Run /sync-feedback --export to generate GitHub issues.
   ```

### Export Mode (--export)

1. **Find reviewed feedback** (status: reviewed):
   ```bash
   grep -l "status: reviewed" ~/.claude/learnings/projects/*/feedback/**/*.md
   ```

2. **For each reviewed item**, generate GitHub issue format:
   ```markdown
   ## Issue: [improvement] Add status filtering to /task-list

   **Type**: improvement
   **Target**: plugins/product-design/commands/task-list.md
   **Source Project**: product-forge

   ### Description
   The /task-list command shows all tasks regardless of status.
   Adding --status flag would help filter to pending/completed items.

   ### Suggested Implementation
   [From feedback description]

   ---
   Captured via Product Forge feedback hooks
   ```

3. **Offer submission options**:
   ```
   5 items ready for export:

   Options:
     [1] Copy to clipboard (one at a time)
     [2] Create GitHub issue via gh CLI
     [3] Export to file (feedback-export.md)
     [4] Cancel

   Select option:
   ```

4. **After export**, move items to `~/.claude/learnings/synced/`

## Feedback File Format

Each feedback file uses YAML frontmatter:

```markdown
---
type: improvement
status: pending
captured: 2026-01-06T15:30:00Z
session_id: abc123
project: my-django-app
repo: https://github.com/user/my-django-app
target: plugins/python-experts/skills/django-api
---

# Add pagination guidance to django-api skill

The django-api skill covers endpoint creation but lacks
guidance on pagination patterns for large datasets.
```

## Status Transitions

```
pending → reviewed → synced
            ↓
         dismissed
```

## Notes

- Feedback stays local until you explicitly export/submit
- Dismissed items are archived, not deleted
- Use `--status` regularly to see accumulated feedback
- The Product Forge team reviews submitted feedback for inclusion
