---
rfc_id: RFC-XXXX
title: [Descriptive Title]
status: DRAFT
author: [Your Name]
reviewers:
  - name: [Reviewer 1]
    status: pending
  - name: [Reviewer 2]
    status: pending
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
decision_date:
related_prds: []
related_rfcs: []
---

# RFC-XXXX: [Title]

## Overview

[1-2 paragraphs summarizing what this RFC proposes, why it matters, and the expected outcome. Keep it concise - details come later.]

## Table of Contents

- [Background & Context](#background--context)
- [Problem Statement](#problem-statement)
- [Goals & Non-Goals](#goals--non-goals)
- [Evaluation Criteria](#evaluation-criteria)
- [Options Analysis](#options-analysis)
- [Recommendation](#recommendation)
- [Technical Design](#technical-design)
- [Security Considerations](#security-considerations)
- [Implementation Plan](#implementation-plan)
- [Open Questions](#open-questions)
- [Decision Record](#decision-record)
- [References](#references)

---

## Background & Context

### Current State

[Describe the current state of the system or process. What exists today?]

### Historical Context

[Any relevant history that led to this RFC. Previous attempts, related changes, etc.]

### Glossary

| Term | Definition |
|------|------------|
| [Term 1] | [Definition] |
| [Term 2] | [Definition] |

---

## Problem Statement

### The Problem

[Clearly articulate the specific problem being addressed. Be precise and measurable where possible.]

### Evidence

[What data, metrics, incidents, or user feedback demonstrates this problem?]

- Evidence point 1
- Evidence point 2
- Evidence point 3

### Impact of Inaction

[What happens if we don't solve this problem? Quantify if possible.]

- Cost: [financial impact]
- Risk: [technical or business risk]
- Opportunity: [what we miss out on]

---

## Goals & Non-Goals

### Goals (In Scope)

1. [Goal 1 - make it measurable]
2. [Goal 2]
3. [Goal 3]

### Non-Goals (Out of Scope)

1. [Explicitly what this RFC does NOT address]
2. [Future work deferred]
3. [Related but separate concerns]

### Success Criteria

How will we know this RFC achieved its goals?

- [ ] [Criterion 1 with measurable target]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

## Evaluation Criteria

The following criteria will be used to objectively evaluate each option:

| Criterion | Weight | Description | Minimum Threshold |
|-----------|--------|-------------|-------------------|
| [Criterion 1] | [High/Medium/Low] | [What this measures] | [If applicable] |
| [Criterion 2] | [High/Medium/Low] | [What this measures] | [If applicable] |
| [Criterion 3] | [High/Medium/Low] | [What this measures] | [If applicable] |
| [Criterion 4] | [High/Medium/Low] | [What this measures] | [If applicable] |
| [Criterion 5] | [High/Medium/Low] | [What this measures] | [If applicable] |

---

## Options Analysis

### Option 1: [Name]

**Description**

[Detailed description of this option and how it would work]

**Advantages**

- [Advantage 1 with evidence/reasoning]
- [Advantage 2]
- [Advantage 3]

**Disadvantages**

- [Disadvantage 1 with evidence/reasoning]
- [Disadvantage 2]
- [Disadvantage 3]

**Evaluation Against Criteria**

| Criterion | Rating | Notes |
|-----------|--------|-------|
| [Criterion 1] | [Score/Rating] | [Justification] |
| [Criterion 2] | [Score/Rating] | [Justification] |
| [Criterion 3] | [Score/Rating] | [Justification] |

**Effort Estimate**

- Complexity: [Low/Medium/High]
- Resources: [Team size, duration estimate]
- Dependencies: [What this depends on]

**Risk Assessment**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [Low/Medium/High] | [Low/Medium/High] | [How to mitigate] |

---

### Option 2: [Name]

**Description**

[Detailed description of this option and how it would work]

**Advantages**

- [Advantage 1 with evidence/reasoning]
- [Advantage 2]
- [Advantage 3]

**Disadvantages**

- [Disadvantage 1 with evidence/reasoning]
- [Disadvantage 2]
- [Disadvantage 3]

**Evaluation Against Criteria**

| Criterion | Rating | Notes |
|-----------|--------|-------|
| [Criterion 1] | [Score/Rating] | [Justification] |
| [Criterion 2] | [Score/Rating] | [Justification] |
| [Criterion 3] | [Score/Rating] | [Justification] |

**Effort Estimate**

- Complexity: [Low/Medium/High]
- Resources: [Team size, duration estimate]
- Dependencies: [What this depends on]

**Risk Assessment**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [Low/Medium/High] | [Low/Medium/High] | [How to mitigate] |

---

### Option 3: [Name] (if applicable)

[Repeat the same structure as above]

---

### Options Comparison Summary

| Criterion | Option 1 | Option 2 | Option 3 |
|-----------|----------|----------|----------|
| [Criterion 1] | [Rating] | [Rating] | [Rating] |
| [Criterion 2] | [Rating] | [Rating] | [Rating] |
| [Criterion 3] | [Rating] | [Rating] | [Rating] |
| **Overall** | [Score] | [Score] | [Score] |

---

## Recommendation

### Recommended Option

**[Option N: Name]**

### Justification

[Explain why this option is recommended based on the evaluation criteria. Be specific about how it scored and why those scores matter for this context.]

### Accepted Trade-offs

[Acknowledge the disadvantages of the recommended option and explain why they are acceptable:]

1. [Trade-off 1]: Acceptable because [reason]
2. [Trade-off 2]: Acceptable because [reason]

### Conditions

[Any conditions or constraints on this recommendation:]

- [Condition 1]
- [Condition 2]

---

## Technical Design

> Note: Complete this section after RFC is approved, or include preliminary design for review.

### Architecture Overview

[High-level architecture diagram - use ASCII art or describe clearly]

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Component A │────▶│ Component B │────▶│ Component C │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Key Components

#### Component 1

- Responsibility: [What it does]
- Technology: [Stack/framework]
- Interfaces: [APIs, protocols]

#### Component 2

[Repeat as needed]

### Data Model

[Entity relationships, schema changes, data flow]

### API Design

[Key API endpoints, request/response formats]

```
POST /api/v1/resource
Request: { ... }
Response: { ... }
```

---

## Security Considerations

### Threat Analysis

| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| [Threat 1] | [High/Medium/Low] | [High/Medium/Low] | [How addressed] |
| [Threat 2] | [High/Medium/Low] | [High/Medium/Low] | [How addressed] |

### Security Measures

- [ ] [Security measure 1]
- [ ] [Security measure 2]
- [ ] [Security measure 3]

### Compliance

[Any regulatory or compliance requirements addressed]

---

## Implementation Plan

### Phases

#### Phase 1: [Name]

- **Scope**: [What's included]
- **Deliverables**: [Concrete outputs]
- **Dependencies**: [What must be ready first]

#### Phase 2: [Name]

[Repeat as needed]

### Milestones

| Milestone | Description | Target | Status |
|-----------|-------------|--------|--------|
| [Milestone 1] | [What it means] | [Date] | Not Started |
| [Milestone 2] | [What it means] | [Date] | Not Started |

### Rollback Strategy

[How to revert if something goes wrong]

---

## Open Questions

Questions that need resolution before or during implementation:

1. **[Question 1]**
   - Context: [Why this matters]
   - Owner: [Who should answer]
   - Status: Open

2. **[Question 2]**
   - Context: [Why this matters]
   - Owner: [Who should answer]
   - Status: Open

---

## Decision Record

> Complete this section after RFC review is concluded.

### Decision

**Status**: [APPROVED / REJECTED / DEFERRED]

**Date**: YYYY-MM-DD

**Approvers**:
- [Name 1]
- [Name 2]

### Decision Summary

[Brief statement of the decision made]

### Key Discussion Points

[Notable points raised during review that influenced the decision]

1. [Point 1]
2. [Point 2]

### Conditions of Approval

[Any conditions or modifications required]

### Dissenting Opinions

[Document any significant disagreements for the record]

---

## References

### Related Documents

- [Document 1](link)
- [Document 2](link)

### External Resources

- [Resource 1](link)
- [Resource 2](link)

### Appendix

[Any supporting materials - detailed diagrams, data, analysis]
