---
name: technical-specification
description: Technical specification writing for implementation details. Use when documenting how to build a solution (post-decision), API contracts, schemas, and system design. Complements RFC skill which handles decision-making.
user-invocable: false
---

# Technical Specification Skill

This skill automatically activates when documenting implementation details for a solution. Unlike RFC (which evaluates options), Tech Specs document **how** to build something when the approach is already decided.

## When This Skill Activates

- Documenting implementation approach after RFC approval
- Writing API specifications and contracts
- Defining database schemas and data models
- Creating system integration specifications
- Documenting component architecture details
- Writing implementation guides for developers

## RFC vs Tech Spec

| Aspect | RFC | Tech Spec |
|--------|-----|-----------|
| **Purpose** | Evaluate options, make decision | Document implementation details |
| **Options Analysis** | Required (min 2) | Not applicable |
| **When Used** | Before decision | After decision (or when no decision needed) |
| **Audience** | Decision makers, stakeholders | Implementers, developers |
| **Lifecycle** | DRAFT → REVIEW → APPROVED → COMPLETED | DRAFT → APPROVED → REFERENCE |

## When to Use Tech Spec (Not RFC)

Use Tech Spec when:
- Decision is already made (via RFC or otherwise)
- Only one viable implementation approach exists
- Documenting API contracts or schemas
- Writing integration specifications
- Creating implementation guides

Use RFC instead when:
- Multiple viable options exist
- Stakeholder buy-in needed
- Decision has cross-team impact
- Choice is costly to reverse

## Tech Spec Document Structure

### Required Sections

1. **Header Metadata**
   ```yaml
   ---
   tech_spec_id: TS-XXXX
   title: [Component/Feature Name]
   status: DRAFT | APPROVED | REFERENCE | ARCHIVED
   decision_ref: RFC-XXXX  # Optional - link to RFC if one exists
   author: [Name]
   created: YYYY-MM-DD
   last_updated: YYYY-MM-DD
   ---
   ```

2. **Executive Summary** (1 paragraph)
   - What is being built
   - Why this approach (brief, reference RFC if applicable)
   - Key design decisions

3. **Design Overview**
   - High-level architecture
   - Component relationships
   - Data flow description

4. **Detailed Specifications**
   For each component:
   - Responsibility
   - Technology stack
   - Key interfaces
   - Implementation notes

5. **Data Model / Schema**
   - Entity definitions
   - Relationships
   - Database schema (if applicable)
   - Migration strategy

6. **API Specification**
   - Endpoints with methods
   - Request/response formats
   - Authentication requirements
   - Error handling

7. **Security Implementation**
   - Authentication mechanism
   - Authorization model
   - Data protection
   - Compliance requirements

8. **Performance Considerations**
   - Throughput/latency targets
   - Caching strategy
   - Optimization approach
   - Monitoring metrics

9. **Testing Strategy**
   - Unit test requirements
   - Integration test scenarios
   - Load testing approach

10. **Deployment & Operations**
    - Deployment process
    - Configuration management
    - Monitoring & alerting
    - Rollback procedure

11. **Dependencies**
    - External services
    - Internal components
    - Third-party libraries

12. **Implementation Checklist**
    - Phased implementation plan
    - Milestones with targets

## Tech Spec Lifecycle

```
DRAFT → APPROVED → REFERENCE
          ↓
       ARCHIVED (when superseded or deprecated)
```

### Status Definitions

| Status | Description |
|--------|-------------|
| **DRAFT** | Being written, not yet reviewed |
| **APPROVED** | Ready for implementation |
| **REFERENCE** | Implementation complete, serves as documentation |
| **ARCHIVED** | Superseded or no longer relevant |

## Relationship to RFC

Tech Specs can optionally link to an RFC:

```yaml
decision_ref: RFC-0042  # Links to the decision that led to this spec
```

**When to link:**
- Tech Spec implements an approved RFC
- Want traceability from decision to implementation

**When standalone is fine:**
- Simple feature that didn't need RFC
- External requirement (no decision to make)
- Standard patterns being applied

## Quality Standards

### Completeness Checklist

Before marking APPROVED:
- [ ] All required sections are filled
- [ ] Architecture diagram is included
- [ ] API endpoints are fully specified
- [ ] Data model is complete
- [ ] Security considerations are addressed
- [ ] Deployment process is documented
- [ ] Implementation phases are defined

### Writing Guidelines

1. **Be Specific**
   - Include concrete details, not vague descriptions
   - Specify exact endpoints, schemas, configurations

2. **Include Examples**
   - API request/response examples
   - Configuration snippets
   - Code patterns to follow

3. **Document Constraints**
   - Performance requirements with numbers
   - Resource limitations
   - Compatibility requirements

4. **Reference Don't Duplicate**
   - Link to RFC for decision rationale
   - Reference existing documentation
   - Avoid copying content that exists elsewhere

## File Naming Convention

```
TS-XXXX-<short-description>.md
```

Examples:
- `TS-0001-user-authentication-api.md`
- `TS-0015-payment-integration.md`
- `TS-0042-cache-layer-design.md`

## Directory Structure

```
tech-specs/
├── draft/              # Work in progress
├── approved/           # Ready for implementation
├── reference/          # Implementation complete
└── archive/            # Superseded/deprecated
    └── YYYY/
```

## Integration with CTO Architect Workflow

The CTO Architect uses this skill for:

1. **Post-RFC Implementation Planning**
   - RFC approved → Create Tech Spec for details
   - Document the "how" after deciding the "what"

2. **Standalone Specifications**
   - Simple features without RFC
   - API contracts and schemas
   - Integration specifications

3. **Delegation to Specialists**
   - Tech Spec provides context for specialist agents
   - Clear specifications enable parallel development

## Commands

| Command | Description |
|---------|-------------|
| `/create-tech-spec <name>` | Create new Tech Spec from template |
| `/list-tech-specs` | List all Tech Specs with status |
| `/tech-spec-status <id>` | View or update Tech Spec status |

## References

- Template: `./references/tech-spec-template.md`
- Checklist: `./references/tech-spec-checklist.md`
