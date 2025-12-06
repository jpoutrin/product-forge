# RFC Management Process

**Comprehensive process for creating, reviewing, and managing technical RFCs (Request for Comments)**

Version: 1.0.0

---

## Overview

This process defines how to systematically manage RFCs throughout their lifecycle, from initial proposal through decision and implementation. It ensures consistent technical decision-making with objective analysis and proper stakeholder involvement.

---

## Directory Structure

### Standard RFC Organization

```
rfcs/
├── draft/              # RFCs being written
├── review/             # Open for stakeholder review
├── approved/           # Approved, awaiting implementation
│   └── in-progress/    # Currently being implemented
├── completed/          # Implementation finished
└── archive/            # Superseded, rejected, or abandoned
    └── YYYY/
        ├── superseded/
        ├── rejected/
        └── abandoned/
```

### File Naming Convention

```
RFC-XXXX-<short-description>.md
```

- `XXXX`: 4-digit sequential number (0001, 0002, etc.)
- `short-description`: Kebab-case summary (max 5 words)

Examples:
- `RFC-0001-api-gateway-selection.md`
- `RFC-0042-database-migration-strategy.md`
- `RFC-0103-authentication-redesign.md`

---

## RFC Lifecycle

### Status Flow

```
           ┌─────────────────────────────────────────────────────┐
           │                                                     │
           ▼                                                     │
        DRAFT ──────────▶ REVIEW ──────────▶ APPROVED           │
           │                 │                   │               │
           │                 │                   ▼               │
           │                 │             IN_PROGRESS           │
           │                 │                   │               │
           │                 ▼                   ▼               │
           │             REJECTED           COMPLETED            │
           │                 │                   │               │
           ▼                 ▼                   ▼               │
       ABANDONED ───────▶ ARCHIVE ◀───────  SUPERSEDED ◀────────┘
```

### Status Definitions

| Status | Location | Description |
|--------|----------|-------------|
| **DRAFT** | `draft/` | Initial writing, author working on content |
| **REVIEW** | `review/` | Open for stakeholder feedback and discussion |
| **APPROVED** | `approved/` | Decision made, ready for implementation |
| **IN_PROGRESS** | `approved/in-progress/` | Implementation actively underway |
| **COMPLETED** | `completed/` | Implementation successfully finished |
| **REJECTED** | `archive/YYYY/rejected/` | Proposal declined after review |
| **ABANDONED** | `archive/YYYY/abandoned/` | Author chose not to proceed |
| **SUPERSEDED** | `archive/YYYY/superseded/` | Replaced by newer RFC |

### Status Transitions

| From | To | Trigger | Required Action |
|------|-----|---------|-----------------|
| DRAFT | REVIEW | Author ready | Set reviewers, notify stakeholders |
| DRAFT | ABANDONED | Author decision | Add abandon reason, move to archive |
| REVIEW | APPROVED | Reviewers approve | Document decision, set decision date |
| REVIEW | REJECTED | Reviewers reject | Document reasons, move to archive |
| REVIEW | DRAFT | Needs revision | Notify author, update feedback |
| APPROVED | IN_PROGRESS | Work begins | Create implementation tracking |
| IN_PROGRESS | COMPLETED | Work finished | Verify completion, update status |
| Any | SUPERSEDED | New RFC created | Link to new RFC, archive |

---

## RFC Creation Process

### Step 1: Initiate RFC

1. **Determine if RFC is needed**
   - Significant architectural change
   - Technology selection decision
   - Cross-team impact
   - Reversibility is difficult or costly

2. **Get next RFC number**
   - Check existing RFCs for highest number
   - Increment by 1

3. **Create from template**
   ```bash
   /create-rfc <short-description>
   ```

### Step 2: Draft RFC

1. **Complete required sections**
   - Overview (what and why)
   - Problem Statement (evidence-based)
   - Goals & Non-Goals (explicit scope)
   - Evaluation Criteria (defined before options)
   - Options Analysis (minimum 2 options)
   - Recommendation (with trade-offs)

2. **Apply objectivity principles**
   - Use neutral language
   - Support claims with evidence
   - Document disadvantages for ALL options
   - Avoid predetermined conclusions

3. **Self-review checklist**
   - [ ] All required sections complete
   - [ ] At least 2 options analyzed
   - [ ] Criteria defined before scoring
   - [ ] Trade-offs acknowledged
   - [ ] Language is objective
   - [ ] Diagrams included where helpful

### Step 3: Submit for Review

1. **Transition to REVIEW status**
   ```bash
   /rfc-status RFC-XXXX --set REVIEW
   ```

2. **Assign reviewers**
   - Technical experts for the domain
   - Stakeholders affected by decision
   - At least 2 reviewers required

3. **Notify stakeholders**
   - Share RFC link
   - Set review deadline
   - Schedule review meeting if needed

### Step 4: Review Process

1. **Reviewers provide feedback**
   - Comment on analysis completeness
   - Challenge assumptions
   - Suggest missing options
   - Verify objectivity

2. **Author addresses feedback**
   - Update RFC based on comments
   - Respond to questions
   - Clarify ambiguities

3. **Iterate until consensus**
   - May require multiple review rounds
   - Document significant discussion points

### Step 5: Decision

1. **Approvers make decision**
   - APPROVED: Proceed with recommendation
   - REJECTED: Document reasons, archive
   - REVISION: Return to DRAFT

2. **Document decision**
   - Fill Decision Record section
   - Record approvers and date
   - Note any conditions

3. **Update status and location**
   ```bash
   /rfc-status RFC-XXXX --set APPROVED
   ```

### Step 6: Implementation

1. **Transition to IN_PROGRESS**
   - Create implementation tasks
   - Link to PRD if applicable
   - Track progress

2. **Complete implementation**
   - Follow technical design
   - Update RFC with learnings
   - Document any deviations

3. **Mark COMPLETED**
   - Verify all goals met
   - Update final status
   - Move to completed directory

---

## Review Guidelines

### For Authors

- **Be open to feedback**: RFCs improve through review
- **Respond promptly**: Keep review momentum
- **Document changes**: Track what was updated based on feedback
- **Separate ego from proposal**: The RFC is about finding the best solution

### For Reviewers

- **Be constructive**: Suggest improvements, not just criticisms
- **Challenge assumptions**: Ask "why" and "how do we know"
- **Check for bias**: Ensure analysis is objective
- **Consider trade-offs**: No solution is perfect
- **Approve when ready**: Don't delay unnecessarily

### Review Checklist

- [ ] Problem statement is clear and evidence-based
- [ ] Scope (goals/non-goals) is explicit
- [ ] Evaluation criteria are sensible for this decision
- [ ] All viable options are considered
- [ ] Analysis is objective and balanced
- [ ] Trade-offs are acknowledged
- [ ] Recommendation follows from analysis
- [ ] Technical design is feasible
- [ ] Security considerations are addressed
- [ ] Implementation plan is realistic

---

## RFC Numbering

### Sequential Numbering

- Start from RFC-0001
- Never reuse numbers
- Gaps are acceptable (rejected/abandoned RFCs keep their numbers)

### Finding Next Number

1. List all existing RFCs:
   ```bash
   /list-rfcs --all
   ```

2. Use next sequential number

### Number Reservation

If working on multiple RFCs simultaneously:
1. Create placeholder in `draft/`
2. Use placeholder number
3. Update when ready for review

---

## Archival Process

### When to Archive

1. **COMPLETED**: After implementation is verified
2. **REJECTED**: After decision is documented
3. **ABANDONED**: When author decides not to proceed
4. **SUPERSEDED**: When new RFC replaces this one

### Archive Metadata

Add to RFC header before archiving:

```yaml
archive_date: YYYY-MM-DD
archive_reason: [completed|rejected|abandoned|superseded]
superseded_by: RFC-XXXX  # if superseded
implementation_status: [full|partial|none]
```

### Archive Structure

```
archive/
└── 2025/
    ├── completed/
    │   └── RFC-0042-database-migration.md
    ├── rejected/
    │   └── RFC-0015-graphql-adoption.md
    ├── abandoned/
    │   └── RFC-0023-microservices-split.md
    └── superseded/
        └── RFC-0008-auth-v1.md
```

---

## Integration with Other Processes

### With PRD Management

```
PRD (What to build)
        │
        ▼
RFC (How to build - technical decisions)
        │
        ▼
Tasks (Implementation)
```

- Link RFC to source PRD in metadata
- Reference RFC in PRD's Technical Requirements section
- Update both when scope changes

### With CTO Architect Workflow

The CTO Architect agent:
1. Reviews PRD requirements
2. Identifies decisions needing RFCs
3. Creates RFC using template
4. Ensures objective analysis
5. Delegates implementation to specialist agents

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/create-rfc <name>` | Create new RFC from template |
| `/list-rfcs` | List all RFCs with status |
| `/rfc-status <id>` | Show or update RFC status |

---

## Best Practices

1. **Write RFCs for significant decisions only**
   - Small changes don't need RFCs
   - If reversible and low-risk, just do it

2. **Complete before review**
   - Don't submit half-finished RFCs
   - Reviewers' time is valuable

3. **Keep RFCs focused**
   - One decision per RFC
   - Split large proposals into multiple RFCs

4. **Update RFCs during implementation**
   - Document deviations from plan
   - Capture learnings for future

5. **Reference, don't duplicate**
   - Link to other docs, don't copy content
   - Keep single source of truth

6. **Archive promptly**
   - Don't let old RFCs linger
   - Clear out completed work regularly

---

## Common Anti-Patterns

### To Avoid

1. **Predetermined Conclusions**
   - Writing RFC to justify a decision already made
   - Fix: Define criteria before analyzing options

2. **Single Option RFC**
   - Only presenting one option
   - Fix: Always include at least 2 viable alternatives

3. **Scope Creep**
   - RFC grows to cover too much
   - Fix: Split into focused RFCs

4. **Endless Review**
   - Review cycles without progress
   - Fix: Set deadlines, make decisions

5. **Implementation Without RFC**
   - Significant changes without documentation
   - Fix: Retroactive RFC or ADR

---

*This RFC management process ensures consistent, objective technical decision-making across the organization.*
