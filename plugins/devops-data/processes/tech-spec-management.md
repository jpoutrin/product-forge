# Technical Specification Management Process

**Process for creating, approving, and maintaining Technical Specifications**

Version: 1.0.0

---

## Overview

This process defines how to manage Technical Specifications throughout their lifecycle. Tech Specs document implementation details for solutions - they describe **how** to build something, not **what** to decide (that's what RFCs are for).

---

## RFC vs Tech Spec

| Document | Purpose | Lifecycle |
|----------|---------|-----------|
| **RFC** | Evaluate options, make decision | DRAFT → REVIEW → APPROVED → COMPLETED |
| **Tech Spec** | Document implementation details | DRAFT → APPROVED → REFERENCE |

### When to Use Each

**Use RFC when:**
- Multiple viable options exist
- Stakeholder buy-in needed
- Decision has cross-team impact

**Use Tech Spec when:**
- Decision is made (or no decision needed)
- Documenting implementation approach
- Writing API/schema specifications

---

## Directory Structure

```
tech-specs/
├── draft/              # Being written
├── approved/           # Ready for implementation
├── reference/          # Implementation complete
└── archive/            # Superseded or deprecated
    └── YYYY/
```

## File Naming Convention

```
TS-XXXX-<short-description>.md
```

Examples:
- `TS-0001-user-authentication-api.md`
- `TS-0015-payment-integration.md`

---

## Tech Spec Lifecycle

### Status Flow

```
DRAFT ─────────────▶ APPROVED ─────────────▶ REFERENCE
(writing)             (ready)                 (implemented)
                         │                         │
                         │                         │
                         ▼                         ▼
                     ARCHIVED ◀────────────────────┘
                     (deprecated)
```

### Status Definitions

| Status | Directory | Description |
|--------|-----------|-------------|
| **DRAFT** | `draft/` | Being written, not ready for implementation |
| **APPROVED** | `approved/` | Complete, ready to implement |
| **REFERENCE** | `reference/` | Implementation finished, serves as documentation |
| **ARCHIVED** | `archive/YYYY/` | Superseded or no longer relevant |

### Status Transitions

| From | To | Trigger | Action |
|------|-----|---------|--------|
| DRAFT | APPROVED | Author ready | Run checklist, move file |
| APPROVED | REFERENCE | Implementation done | Add implementation link |
| APPROVED | ARCHIVED | Plan changed | Add archive reason |
| REFERENCE | ARCHIVED | Superseded | Link to replacement |

---

## Creation Process

### Step 1: Determine Need

Ask:
- Is the approach already decided? → Tech Spec
- Need to evaluate options? → RFC first

### Step 2: Create Spec

```bash
# Standalone spec
/create-tech-spec <title>

# Spec implementing an RFC
/create-tech-spec <title> --rfc RFC-XXXX
```

### Step 3: Write Spec

Complete all sections using template:
1. Executive Summary
2. Design Overview (with diagram)
3. Detailed Specifications
4. Data Model
5. API Specification
6. Security Implementation
7. Performance Considerations
8. Testing Strategy
9. Deployment & Operations
10. Dependencies
11. Implementation Checklist

### Step 4: Quality Check

Run through checklist:
- All sections complete
- No placeholders remaining
- Diagrams included
- Examples provided
- Specific (not vague)

### Step 5: Approve

```bash
/tech-spec-status TS-XXXX --set APPROVED
```

---

## Approval Criteria

Before marking APPROVED, verify:

### Completeness
- [ ] All required sections filled
- [ ] No placeholder text
- [ ] Architecture diagram present

### Specificity
- [ ] Technology versions specified
- [ ] API endpoints fully documented
- [ ] Data model complete with types

### Implementability
- [ ] Developer could implement from spec alone
- [ ] No missing critical details
- [ ] Constraints clearly stated

### Quality
- [ ] Consistent terminology
- [ ] Examples provided
- [ ] External links valid

---

## Implementation Tracking

### During Implementation

The APPROVED spec guides implementation:
- Developers reference for architecture
- API contracts serve as source of truth
- Data model defines schema

### After Implementation

When implementation is complete:

```bash
/tech-spec-status TS-XXXX --set REFERENCE
```

Add to spec:
- Link to implementation (repo, PR)
- Note any deviations from original design
- Lessons learned

---

## Archival

### When to Archive

Archive Tech Specs when:
1. Replaced by newer specification
2. Feature/component deprecated
3. No longer relevant

### Archive Process

```bash
/tech-spec-status TS-XXXX --set ARCHIVED
```

Add to metadata:
```yaml
archive_date: YYYY-MM-DD
archive_reason: [superseded|deprecated|obsolete]
superseded_by: TS-XXXX  # if applicable
```

---

## Relationship to RFC

### Linked Specs

Tech Specs can optionally link to RFCs:

```yaml
decision_ref: RFC-0042
```

### Workflow Integration

```
PRD (What to build)
         │
         ▼
    RFC Needed? ────────────────┐
         │                      │
    YES  │                 NO   │
         ▼                      │
       RFC                      │
    (decide approach)           │
         │                      │
         ▼                      │
    APPROVED                    │
         │                      │
         ▼                      ▼
    Tech Spec ◀─────────────────┘
    (document how)
    [optional RFC link]
         │
         ▼
    Implementation
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/create-tech-spec <name>` | Create new spec from template |
| `/list-tech-specs` | List all specs with status |
| `/tech-spec-status <id>` | View or update spec status |

---

## Best Practices

1. **One Component Per Spec**
   - Keep specs focused
   - Split large systems into multiple specs

2. **Include Diagrams**
   - Architecture overview required
   - Data flow diagrams helpful
   - Sequence diagrams for complex flows

3. **Be Specific**
   - No vague language ("as appropriate")
   - Include concrete examples
   - Specify versions and configurations

4. **Keep Updated**
   - Update during implementation if design changes
   - Document deviations from original plan
   - Transition to REFERENCE when done

5. **Link Related Docs**
   - Reference RFC if one exists
   - Link to PRD for context
   - Point to implementation when complete

---

## Integration with CTO Architect

The CTO Architect agent uses Tech Specs to:

1. **Document Approved Decisions**
   - After RFC approval, create Tech Spec
   - Fill in implementation details

2. **Guide Specialist Agents**
   - Tech Spec provides context for delegation
   - API specs enable parallel work

3. **Track Implementation**
   - Spec status shows progress
   - Deviations documented

---

*This process ensures implementation details are properly documented and maintained throughout the development lifecycle.*
