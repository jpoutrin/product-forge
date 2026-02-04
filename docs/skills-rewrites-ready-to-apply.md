# Skills Rewrites - Ready to Apply

This document contains specific, ready-to-apply rewrites for your skills. Each section shows the exact changes to make.

## Quick Reference: Two Key Improvements

1. **Add `user-invocable: false`** to knowledge/reference skills
2. **Rewrite descriptions** with natural trigger phrases users would actually say

---

## Knowledge Skills: Add user-invocable: false

These skills should auto-invoke when relevant, not require explicit user request.

### 1. mcp-architecture

**File**: `plugins/devops-data/skills/mcp-architecture/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: mcp-architecture
description: MCP (Model Context Protocol) architecture patterns, security best practices, and memory management strategies. Use when designing, implementing, or debugging MCP servers in Python (FastMCP) or TypeScript.
---
```

**To**:
```yaml
---
name: mcp-architecture
description: MCP architecture patterns, security, and memory management. Auto-loads when building MCP servers, implementing tools/resources, discussing MCP security, or working with FastMCP.
user-invocable: false
---
```

### 2. django-dev

**File**: `plugins/python-experts/skills/django-dev/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: django
description: Django web application development (2025). Use when creating or modifying Django projects, apps, models, views, URLs, forms, templates, or management commands. Covers project structure, naming conventions, async support, type hints, and modern best practices.
---
```

**To**:
```yaml
---
name: django
description: Django development patterns and conventions (2025). Auto-loads when working with Django models, views, URLs, forms, templates, management commands, or project structure. Includes async support and type hints.
user-invocable: false
---
```

### 3. python-style

**File**: `plugins/python-experts/skills/python-style/SKILL.md`

**Change frontmatter to**:
```yaml
---
name: python-style
description: Python coding style enforcement (PEP standards, type hints, docstrings, modern patterns). Auto-loads when writing or reviewing Python code.
user-invocable: false
---
```

### 4. typescript-style

**File**: `plugins/frontend-experts/skills/typescript-style/SKILL.md`

**Change frontmatter to**:
```yaml
---
name: typescript-style
description: TypeScript coding style enforcement (ESLint, type safety, React patterns). Auto-loads when writing or reviewing TypeScript/JavaScript code.
user-invocable: false
---
```

### 5. qa-testing-methodology

**File**: `plugins/product-design/skills/qa-testing-methodology/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: qa-testing-methodology
description: QA best practices and test design patterns. Use when designing test cases to ensure comprehensive coverage with equivalence partitioning, boundary analysis, and accessibility testing.
---
```

**To**:
```yaml
---
name: qa-testing-methodology
description: QA test design patterns (equivalence partitioning, boundary analysis, accessibility). Auto-loads when designing test cases, planning test coverage, or writing test procedures.
user-invocable: false
---
```

### 6. documentation-research

**File**: `plugins/python-experts/skills/documentation-research/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: documentation-research
description: Enforces online documentation research before any technical implementation. Use when implementing features to ensure code follows current best practices by researching official documentation first.
---
```

**To**:
```yaml
---
name: documentation-research
description: Enforces documentation research before implementation. Auto-loads when implementing features to ensure current best practices are followed. Researches official docs first.
user-invocable: false
---
```

### 7. pattern-detection

**File**: `plugins/claude-code-dev/skills/pattern-detection/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: pattern-detection
short: Recognize reusable patterns for Product Forge
description: Identify reusable patterns, best practices, and workflow automations during implementation that could become Product Forge skills, commands, or templates. Use when implementing repetitive structures, applying consistent conventions, or recognizing generalizable solutions.
when: Claude implements similar patterns multiple times, creates reusable structures, or applies best practices that could benefit others
---
```

**To**:
```yaml
---
name: pattern-detection
short: Recognize reusable patterns for Product Forge
description: Auto-detects reusable patterns, best practices, and automation opportunities during implementation. Recognizes repetitive structures and generalizable solutions that could become skills.
user-invocable: false
---
```

### 8. python-code-review

**File**: `plugins/python-experts/skills/python-code-review/SKILL.md`

**Change frontmatter to**:
```yaml
---
name: python-code-review
description: Python code review guidelines (security, performance, bugs, style). Auto-loads when reviewing Python code or analyzing code quality.
user-invocable: false
---
```

### 9. typescript-code-review

**File**: `plugins/frontend-experts/skills/typescript-code-review/SKILL.md`

**Change frontmatter to**:
```yaml
---
name: typescript-code-review
description: TypeScript and React code review guidelines (type safety, React patterns, performance). Auto-loads when reviewing TypeScript/React code.
user-invocable: false
---
```

---

## Action Skills: Rewrite Descriptions

These skills should be user-invocable but need better trigger phrases.

### 10. prd-management

**File**: `plugins/product-design/skills/prd-management/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: prd-management
description: Automatic PRD lifecycle management, organization, and status tracking. Use when working with Product Requirements Documents (PRDs) or Feature Requirements Documents (FRDs) for proper naming, directory structure, and status transitions.
---
```

**To**:
```yaml
---
name: prd-management
description: Use when organizing PRDs, tracking requirements, managing product specs, updating PRD status, archiving completed docs, or setting up PRD structure. Auto-applies naming conventions and lifecycle management.
---
```

### 11. parallel-agents

**File**: `plugins/product-design/skills/parallel-agents/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: parallel-agents
short: Orchestrate parallel multi-agent development
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
when: User wants to parallelize development, run multiple agents simultaneously, decompose a PRD into independent tasks, scale work across concurrent workstreams, or coordinate multi-agent workflows
---
```

**To**:
```yaml
---
name: parallel-agents
short: Orchestrate parallel multi-agent development
description: Use when parallelizing development, running multiple agents, splitting work across agents, coordinating parallel tasks, or decomposing PRDs for concurrent execution. Breaks work into independent agent workstreams.
---
```

**Note**: Remove the `when:` field, it's redundant with description.

### 12. mcp-security

**File**: `plugins/security-compliance/skills/mcp-security/SKILL.md`

**Change frontmatter from**:
```yaml
---
name: mcp-security
description: Multi-agent and MCP pipeline security with 5-layer defense architecture. Use when building MCP servers, multi-agent systems, or any pipeline that handles user input to prevent prompt injection and ensure proper authorization.
---
```

**To**:
```yaml
---
name: mcp-security
description: Use when securing MCP servers, preventing prompt injection, implementing authorization, validating user input, or building secure multi-agent pipelines. Provides 5-layer defense architecture patterns.
---
```

### 13. parallel-decompose

**File**: `plugins/product-design/skills/parallel-decompose/SKILL.md`

**Current**:
```yaml
---
name: parallel-decompose
description: Decompose PRDs and Tech Specs into parallel-executable tasks with contracts, prompts, and dependency management. Use when breaking down work into independent parallel tasks.
---
```

**Improved**:
```yaml
---
name: parallel-decompose
description: Use when breaking down PRDs, decomposing tech specs, creating parallel tasks, defining task contracts, or generating agent prompts. Converts specifications into parallel-executable work.
---
```

### 14. network-inspection

**File**: `plugins/product-design/skills/network-inspection/SKILL.md`

**Current**:
```yaml
---
name: network-inspection
description: HTTP request and response analysis for debugging API calls, identifying failed requests, and inspecting network traffic.
---
```

**Improved**:
```yaml
---
name: network-inspection
description: Use when debugging API calls, checking network requests, inspecting HTTP traffic, finding failed requests, analyzing response data, or investigating API errors. Provides detailed request/response analysis.
---
```

### 15. console-debugging

**File**: `plugins/product-design/skills/console-debugging/SKILL.md`

**Current**:
```yaml
---
name: console-debugging
description: Browser console message analysis for debugging JavaScript errors, warnings, and application logs.
---
```

**Improved**:
```yaml
---
name: console-debugging
description: Use when debugging JavaScript errors, checking console warnings, analyzing browser logs, finding runtime errors, investigating console output, or troubleshooting browser issues. Provides console message analysis.
---
```

### 16. qa-test-management

**File**: `plugins/product-design/skills/qa-test-management/SKILL.md`

**Current**:
```yaml
---
name: qa-test-management
description: Automatic QA test lifecycle management, naming conventions, and directory structure. Use when creating, organizing, or managing QA test procedures.
---
```

**Improved**:
```yaml
---
name: qa-test-management
description: Use when creating QA tests, organizing test procedures, managing test lifecycle, updating test status, or archiving completed tests. Auto-applies naming conventions and directory structure.
---
```

### 17. product-strategy

**File**: `plugins/product-design/skills/product-strategy/SKILL.md`

**Current**:
```yaml
---
name: product-strategy
description: Chief Product Officer expertise with proven frameworks and strategic guidance. Use when discussing product vision, conducting discovery, validating market fit, planning roadmaps, or making build-vs-buy decisions.
---
```

**Improved**:
```yaml
---
name: product-strategy
description: Use when planning product strategy, defining product vision, validating market fit, prioritizing features, creating roadmaps, making build-vs-buy decisions, or conducting product discovery. Provides CPO-level frameworks.
---
```

### 18. design-system

**File**: `plugins/product-design/skills/design-system/SKILL.md`

**Current**:
```yaml
---
name: design-system
description: Design system management for building and reusing UI components, tokens, and patterns. Use when creating component libraries or establishing design standards.
---
```

**Improved**:
```yaml
---
name: design-system
description: Use when building component libraries, creating design tokens, establishing design standards, documenting UI patterns, or managing design systems. Ensures consistency and reusability.
---
```

### 19. parallel-task-format

**File**: `plugins/product-design/skills/parallel-task-format/SKILL.md`

**Current**:
```yaml
---
name: parallel-task-format
description: Compact YAML format for defining parallel task specifications with scope, boundaries, and agent selection. Use when creating task specs for parallel execution.
---
```

**Improved**:
```yaml
---
name: parallel-task-format
description: Use when defining parallel tasks, writing task specs, specifying task scope, setting task boundaries, or selecting agents for tasks. Provides compact YAML task format.
---
```

### 20. task-orchestration

**File**: `plugins/product-design/skills/task-orchestration/SKILL.md`

**Current**:
```yaml
---
name: task-orchestration
description: Documentation-first task execution with quality checks and progress tracking. Use when working with structured task lists.
---
```

**Improved**:
```yaml
---
name: task-orchestration
description: Use when executing task lists, tracking task progress, managing task workflows, or ensuring documentation-first development. Provides quality checks and progress tracking.
---
```

---

## Additional Skills That Need Review

These skills have good descriptions but could be slightly improved:

### django-api
```yaml
description: Use when building Django APIs, creating REST endpoints, implementing authentication, or choosing between Django Ninja (modern, async) and DRF (mature, established). Covers both frameworks.
```

### oauth
```yaml
description: Use when implementing OAuth 2.0, adding authentication, integrating with identity providers, configuring OIDC, or securing API access. Covers authorization flows and security patterns.
```

### privacy-compliance
```yaml
description: Use when handling personal data, ensuring GDPR compliance, implementing CCPA requirements, creating privacy policies, or managing user consent. Covers multi-region compliance.
```

### dbt
```yaml
description: Use when building dbt models, writing data transformations, setting up dbt projects, creating tests, or documenting data pipelines. Covers modern analytics engineering patterns.
```

### sqlmesh
```yaml
description: Use when using SQLMesh, setting up virtual environments, tracking column lineage, writing data transformations, or migrating from dbt. Covers SQLMesh-specific patterns.
```

---

## Implementation Checklist

### Phase 1: Knowledge Skills (Quick Wins)
- [ ] Add `user-invocable: false` to 9 knowledge skills (list above)
- [ ] Test: These should auto-load when working with related code
- [ ] Run `/forge-refresh --force`

### Phase 2: Top Action Skills
- [ ] Rewrite top 10 most-used action skill descriptions
- [ ] Test: Ask questions using trigger phrases
- [ ] Monitor which skills invoke more frequently

### Phase 3: Remaining Skills
- [ ] Audit remaining 50+ skills
- [ ] Apply pattern systematically
- [ ] Document usage patterns

### Phase 4: Validation
- [ ] Ask sample questions to test matching
- [ ] Check if skills auto-invoke appropriately
- [ ] Iterate based on real usage

---

## Testing Your Changes

After applying rewrites, test with these user questions:

### For PRD Management:
- "Help me organize my PRD"
- "Track my product requirements"
- "Update PRD status"
- "Archive this completed PRD"

### For Parallel Agents:
- "Run multiple agents on this"
- "Split this work across agents"
- "Parallelize this development"
- "Coordinate parallel tasks"

### For MCP Security:
- "Secure my MCP server"
- "Prevent prompt injection"
- "Add authorization to my MCP"
- "Validate user input"

### For Django (Knowledge - Should Auto-Load):
- "Create a Django model"
- "Add a view to my Django app"
- "Write a management command"
- Should auto-load WITHOUT explicit mention

---

## Batch Script for Knowledge Skills

Here's a script to update all knowledge skills at once:

```bash
#!/bin/bash
# update-knowledge-skills.sh

# Array of knowledge skill paths
declare -a skills=(
    "plugins/devops-data/skills/mcp-architecture/SKILL.md"
    "plugins/python-experts/skills/django-dev/SKILL.md"
    "plugins/python-experts/skills/python-style/SKILL.md"
    "plugins/frontend-experts/skills/typescript-style/SKILL.md"
    "plugins/product-design/skills/qa-testing-methodology/SKILL.md"
    "plugins/python-experts/skills/documentation-research/SKILL.md"
    "plugins/claude-code-dev/skills/pattern-detection/SKILL.md"
    "plugins/python-experts/skills/python-code-review/SKILL.md"
    "plugins/frontend-experts/skills/typescript-code-review/SKILL.md"
)

for skill in "${skills[@]}"; do
    echo "Processing: $skill"
    # Add user-invocable: false after description line
    # This is pseudocode - actual implementation would use sed or similar
done

echo "Done! Run: /forge-refresh --force"
```

---

## Monitoring & Iteration

After applying changes:

1. **Track which skills invoke** - Keep notes on which skills trigger naturally
2. **Collect user feedback** - Ask team members what phrases they use
3. **Review patterns** - After 1 week, analyze which descriptions worked
4. **Iterate** - Update descriptions based on real usage patterns
5. **Document learnings** - Add to this guide for future skills
