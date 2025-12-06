# Technical Specification Checklist

Quality checklist for Technical Specifications before marking as APPROVED.

## Document Completeness

### Required Sections

- [ ] **Header Metadata** is complete
  - [ ] Tech Spec ID assigned (TS-XXXX)
  - [ ] Title is descriptive
  - [ ] Author identified
  - [ ] Dates set
  - [ ] RFC linked (if applicable)

- [ ] **Executive Summary** is written
  - [ ] Explains what is being built
  - [ ] States why this approach (or references RFC)
  - [ ] Highlights key design decisions

- [ ] **Design Overview** is complete
  - [ ] Architecture diagram included
  - [ ] Component relationships described
  - [ ] Data flow documented

- [ ] **Detailed Specifications** for each component
  - [ ] Responsibility defined
  - [ ] Technology stack specified
  - [ ] Key interfaces documented
  - [ ] Implementation notes included

- [ ] **Data Model** is defined
  - [ ] All entities documented
  - [ ] Field types and constraints specified
  - [ ] Relationships diagrammed
  - [ ] Migration strategy (if applicable)

- [ ] **API Specification** is complete (if applicable)
  - [ ] All endpoints documented
  - [ ] Request/response formats shown
  - [ ] Error codes defined
  - [ ] Authentication documented

- [ ] **Security Implementation** is addressed
  - [ ] Authentication mechanism specified
  - [ ] Authorization model defined
  - [ ] Data protection approach documented
  - [ ] Compliance requirements listed

- [ ] **Performance Considerations** are documented
  - [ ] Targets defined with metrics
  - [ ] Caching strategy specified
  - [ ] Optimization approach outlined
  - [ ] Monitoring metrics identified

- [ ] **Testing Strategy** is defined
  - [ ] Unit test coverage target set
  - [ ] Integration test scenarios listed
  - [ ] Load testing approach specified

- [ ] **Deployment & Operations** is documented
  - [ ] Deployment process defined
  - [ ] Configuration variables listed
  - [ ] Monitoring & alerting configured
  - [ ] Rollback procedure documented

- [ ] **Dependencies** are listed
  - [ ] External services identified
  - [ ] Internal components documented
  - [ ] Third-party libraries specified

- [ ] **Implementation Checklist** is created
  - [ ] Phases defined
  - [ ] Tasks identified
  - [ ] Target dates set

## Quality Standards

### Specificity Check

- [ ] No vague language ("appropriate", "as needed", "TBD")
- [ ] All numbers are concrete (latency, throughput, coverage)
- [ ] Technology choices are explicit (versions included)
- [ ] API examples include actual payloads

### Diagram Check

- [ ] At least one architecture diagram included
- [ ] Diagrams are readable (ASCII or Mermaid)
- [ ] Component relationships are clear
- [ ] Data flow direction is shown

### Implementability Check

- [ ] A developer could implement from this spec alone
- [ ] No missing critical decisions
- [ ] Technology choices are justified
- [ ] Constraints are clearly stated

### Consistency Check

- [ ] Terminology is consistent throughout
- [ ] Field names match between sections
- [ ] API endpoints match data model
- [ ] Diagram matches text descriptions

## Before Marking APPROVED

### Final Review

- [ ] All required sections are complete
- [ ] No placeholder text remains
- [ ] Links to external docs are valid
- [ ] RFC is linked (if one exists)
- [ ] Implementation checklist is actionable

### Stakeholder Sign-off

- [ ] Technical lead has reviewed
- [ ] Security has reviewed (if needed)
- [ ] DevOps has reviewed deployment section
- [ ] QA has reviewed testing strategy

## Post-Implementation

### Transition to REFERENCE

When implementation is complete:

- [ ] Update status to REFERENCE
- [ ] Add link to implementation (repo, PR)
- [ ] Document any deviations from original spec
- [ ] Note lessons learned

### Archival

When superseded or deprecated:

- [ ] Update status to ARCHIVED
- [ ] Add archive_date and reason
- [ ] Link to replacement spec (if any)
- [ ] Move to archive directory

## Quick Reference

### Status Transitions

```
DRAFT ──────────────▶ APPROVED
(writing)              (ready to implement)
                           │
                           ▼
                       REFERENCE
                       (implemented)
                           │
                           ▼
                       ARCHIVED
                       (superseded)
```

### File Naming

```
TS-XXXX-<short-description>.md

Examples:
- TS-0001-user-authentication-api.md
- TS-0015-payment-integration.md
- TS-0042-cache-layer-design.md
```

### Directory Structure

```
tech-specs/
├── draft/      # Status: DRAFT
├── approved/   # Status: APPROVED
├── reference/  # Status: REFERENCE
└── archive/    # Status: ARCHIVED
    └── YYYY/
```
