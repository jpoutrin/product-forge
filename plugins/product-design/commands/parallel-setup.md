---
description: Initialize .claude/ infrastructure for parallel multi-agent development
argument-hint: "[--tech django|typescript|go]"
---

# parallel-setup

**Category**: Parallel Development

## Usage

```bash
/parallel-setup [--tech django|typescript|go]
```

## Arguments

- `--tech`: Optional - Technology stack for contract templates (default: auto-detect)

## Purpose

Initialize the `.claude/` orchestration directory structure for parallel multi-agent development. This is the foundation command that must run before decomposition.

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Create Directory Structure

```bash
mkdir -p .claude/{tasks,contracts}
```

Creates:
```
.claude/
├── tasks/              # Task specifications (empty initially)
├── contracts/          # Shared interfaces
├── architecture.md     # System design template
└── readiness-report.md # Placeholder for assessment
```

### 2. Detect Technology Stack

Check for technology indicators:
- **Django**: `manage.py`, `settings.py`, `apps/` directory
- **TypeScript**: `tsconfig.json`, `package.json` with TypeScript
- **Go**: `go.mod`, `main.go`

### 3. Create Contract Templates

**For Django/Python**:
Create `.claude/contracts/types.py`:
```python
"""
Shared domain types for all parallel agents.

IMPORTANT: Changes here affect ALL parallel tasks.
Coordinate before modifying.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypedDict


# === Entities ===
# Define shared domain entities here


# === Enums ===
# Define shared enums here


# === API Types ===
class PaginationMeta(TypedDict):
    page: int
    total: int
    per_page: int


class ApiResponse(TypedDict):
    data: dict | list
    meta: PaginationMeta | None


class ApiError(TypedDict):
    code: str
    message: str
    details: dict | None
```

**For TypeScript**:
Create `.claude/contracts/types.ts`:
```typescript
/**
 * Shared domain types for all parallel agents.
 *
 * IMPORTANT: Changes here affect ALL parallel tasks.
 * Coordinate before modifying.
 */

// === Entities ===


// === API Types ===
export interface ApiResponse<T> {
  data: T;
  meta?: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  total: number;
  perPage: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
```

### 4. Create OpenAPI Template

Create `.claude/contracts/api-schema.yaml`:
```yaml
openapi: 3.0.3
info:
  title: Project API
  version: 1.0.0
  description: API contract for parallel development

paths:
  # Define endpoints here during decomposition

components:
  schemas:
    # Define schemas here during decomposition

    ApiError:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object

    PaginationMeta:
      type: object
      properties:
        page:
          type: integer
        total:
          type: integer
        per_page:
          type: integer
```

### 5. Create Architecture Template

Create `.claude/architecture.md`:
```markdown
# System Architecture

## Overview
[High-level system description - fill during decomposition]

## Components
| Component | Responsibility | Owner Task |
|-----------|----------------|------------|
| | | |

## Data Flow
[How data moves through the system]

## Boundaries
[Where parallel work can happen safely]

## External Dependencies
[Databases, caches, external APIs, task queues]

## Contracts
- `.claude/contracts/types.py` (or `.ts`)
- `.claude/contracts/api-schema.yaml`
```

### 6. Create Readiness Report Placeholder

Create `.claude/readiness-report.md`:
```markdown
# Parallelization Readiness Report

> Run `/parallel-ready` to populate this report.

## Overall Score: Not Yet Assessed

Run the assessment command for your technology:
- Django: `/parallel-ready-django`
- TypeScript: `/parallel-ready-ts`
```

### 7. Create CLAUDE.md (if missing)

If `CLAUDE.md` doesn't exist at project root, create a basic template based on detected technology. Reference the skill `infrastructure-setup.md` for full CLAUDE.md templates.

### 8. Report Results

Output summary:
```
✅ Created .claude/ directory structure
✅ Created contract templates for [technology]
✅ Created architecture.md template
✅ Created readiness-report.md placeholder
[✅ Created CLAUDE.md | ⚠️ CLAUDE.md already exists]

Next steps:
1. Run /parallel-ready-[tech] to assess codebase
2. Run /parallel-fix-[tech] if score < 80
3. Run /parallel-decompose <prd-file> to create tasks
```

## Example

```bash
# Auto-detect technology
/parallel-setup

# Specify Django
/parallel-setup --tech django

# Specify TypeScript
/parallel-setup --tech typescript
```

## Notes

- This command is idempotent - safe to run multiple times
- Existing files are NOT overwritten
- Works with any technology stack
- Creates foundation for `/parallel-decompose` command
