# Skills Matching Analysis & Recommendations

## Executive Summary

After analyzing your skills against 2026 best practices, the primary issue is that **skill descriptions don't use natural language that users would actually say**. Claude Code's skill matching is pure language model-based—no embeddings, classifiers, or pattern matching. Claude reads skill descriptions and uses native language understanding to match user intent.

**Key insight**: The description field is the most critical part of a skill. It must include 3-5 specific phrases users would naturally say.

## Research Findings: How Skills Matching Works

### No Algorithmic Routing
- Claude Code has no intent classification or pattern matching at the code level
- All available skills are formatted into the Skill tool's prompt
- Claude's language model reads this list and matches user intent naturally
- **Implication**: Write descriptions as if explaining to Claude when to use the skill

### Description Best Practices

1. **Include 3-5 trigger phrases** users would actually say
   - Good: "set up project memory", "track our decisions", "log a bug fix"
   - Bad: "Project memory management system for context persistence"

2. **Test with "Would I actually say this?"**
   - Good: "help me test this feature", "write test cases for the login page"
   - Bad: "initialize comprehensive test coverage subsystem"

3. **Action-oriented language**
   - Good: "Use when creating PRDs", "Use when testing features"
   - Bad: "Provides PRD management capabilities", "Testing methodology framework"

4. **Keep SKILL.md body under 500 lines**
   - Split complex content to sub-files
   - Use progressive disclosure

### Control Fields

```yaml
---
name: skill-name
description: When this skill triggers
disable-model-invocation: true   # Only user can invoke (for side effects)
user-invocable: false            # Only Claude can invoke (background knowledge)
---
```

## Common Issues in Your Skills

### Issue 1: Technical/Jargon-Heavy Descriptions

**Current problems**:
- "Automatic PRD lifecycle management, organization, and status tracking"
- "Multi-agent and MCP pipeline security with 5-layer defense architecture"
- "Enforces online documentation research before any technical implementation"

**Users actually say**:
- "help me organize my PRD" / "track my product requirements"
- "secure my MCP server" / "prevent prompt injection"
- "research best practices for Django" / "look up FastAPI docs"

### Issue 2: Missing Trigger Phrases

Most skills use only "Use when..." without including actual user phrases.

**Example - Current**:
```yaml
description: Automatic PRD lifecycle management, organization, and status tracking. Use when working with Product Requirements Documents (PRDs) or Feature Requirements Documents (FRDs) for proper naming, directory structure, and status transitions.
```

**Improved**:
```yaml
description: Use when organizing PRDs, tracking requirements, managing product documents, updating PRD status, or archiving completed specs. Auto-applies naming conventions and lifecycle management.
```

### Issue 3: Knowledge Skills Without user-invocable: false

These skills are reference material that Claude should auto-invoke:
- `mcp-architecture` - MCP patterns and security
- `django-dev` - Django conventions and patterns
- `qa-testing-methodology` - Test design patterns
- `python-style` - Python coding standards
- `documentation-research` - Research enforcement

**These should have**:
```yaml
user-invocable: false
```

### Issue 4: Side-Effect Skills Without disable-model-invocation: true

Some skills perform destructive operations and should only be user-invoked:
- Git operations (commit, rebase, etc.) ✅ Already have this
- Deployment operations
- Database migrations
- Plugin installation

### Issue 5: Long, Compound Descriptions

**Current example**:
```yaml
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
```

**Problem**: Tries to cover everything in one sentence. Users won't say these exact phrases.

**Better approach**:
```yaml
description: Use when parallelizing development, running multiple agents, splitting work across agents, or coordinating parallel tasks. Decomposes PRDs into independent agent workstreams.
```

## Skill-by-Skill Recommendations

### Knowledge Skills (Set user-invocable: false)

These provide background knowledge and should auto-invoke when relevant:

#### mcp-architecture
```yaml
---
name: mcp-architecture
description: MCP architecture patterns, security, and memory management. Auto-loads when building MCP servers, implementing MCP tools/resources, or discussing MCP security.
user-invocable: false
---
```

#### django-dev
```yaml
---
name: django
description: Django development patterns for 2025. Auto-loads when working with Django models, views, URLs, forms, templates, or management commands.
user-invocable: false
---
```

#### python-style
```yaml
---
name: python-style
description: Python coding style enforcement (PEP standards, type hints, modern patterns). Auto-loads when writing or reviewing Python code.
user-invocable: false
---
```

#### qa-testing-methodology
```yaml
---
name: qa-testing-methodology
description: QA test design patterns (equivalence partitioning, boundary analysis, accessibility). Auto-loads when designing test cases or writing test procedures.
user-invocable: false
---
```

#### documentation-research
```yaml
---
name: documentation-research
description: Enforces documentation research before implementation. Auto-loads when implementing features to ensure current best practices are followed.
user-invocable: false
---
```

### Action Skills (Improve Descriptions)

#### prd-management
**Current**:
```yaml
description: Automatic PRD lifecycle management, organization, and status tracking. Use when working with Product Requirements Documents (PRDs) or Feature Requirements Documents (FRDs) for proper naming, directory structure, and status transitions.
```

**Improved**:
```yaml
description: Use when organizing PRDs, tracking product requirements, managing feature specs, updating PRD status, archiving completed docs, or setting up PRD structure. Enforces naming conventions and lifecycle transitions automatically.
```

**Trigger phrases added**: "organizing PRDs", "tracking product requirements", "managing feature specs", "updating PRD status", "archiving completed docs"

#### parallel-agents
**Current**:
```yaml
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
```

**Improved**:
```yaml
description: Use when parallelizing development, running multiple agents, splitting work across agents, coordinating parallel tasks, or decomposing PRDs for concurrent execution. Breaks down work into independent agent workstreams.
```

**Trigger phrases added**: "parallelizing development", "running multiple agents", "splitting work", "coordinating parallel tasks"

#### mcp-security
**Current**:
```yaml
description: Multi-agent and MCP pipeline security with 5-layer defense architecture. Use when building MCP servers, multi-agent systems, or any pipeline that handles user input to prevent prompt injection and ensure proper authorization.
```

**Improved**:
```yaml
description: Use when securing MCP servers, preventing prompt injection, implementing authorization, validating user input, or building multi-agent pipelines. Provides 5-layer defense architecture and security patterns.
```

**Trigger phrases added**: "securing MCP servers", "preventing prompt injection", "implementing authorization", "validating user input"

#### qa-testing-methodology (if keeping as action skill)
**Current**:
```yaml
description: QA best practices and test design patterns. Use when designing test cases to ensure comprehensive coverage with equivalence partitioning, boundary analysis, and accessibility testing.
```

**Improved**:
```yaml
description: Use when designing test cases, planning QA tests, ensuring test coverage, writing test scenarios, or applying test design patterns. Includes equivalence partitioning, boundary analysis, and accessibility guidelines.
```

**Trigger phrases added**: "designing test cases", "planning QA tests", "ensuring test coverage", "writing test scenarios"

#### pattern-detection
**Current**:
```yaml
description: Identify reusable patterns, best practices, and workflow automations during implementation that could become Product Forge skills, commands, or templates. Use when implementing repetitive structures, applying consistent conventions, or recognizing generalizable solutions.
when: Claude implements similar patterns multiple times, creates reusable structures, or applies best practices that could benefit others
```

**Improved**:
```yaml
description: Auto-detects reusable patterns, best practices, and automation opportunities during implementation. Use when implementing repetitive structures, recognizing generalizable solutions, or applying consistent conventions that could become skills.
user-invocable: false
```

**Rationale**: This should auto-invoke during work, not require explicit user request.

### Command Skills (Already well-designed)

Your command skills like `/parallel-decompose`, `/create-prd`, etc. are well-designed because:
1. They have clear, action-oriented names
2. Users explicitly invoke them with slash commands
3. They don't rely on description matching

## Priority Action Items

### High Priority (Do First)

1. **Add `user-invocable: false` to knowledge skills**
   - [ ] `mcp-architecture`
   - [ ] `django-dev`
   - [ ] `python-style`
   - [ ] `qa-testing-methodology`
   - [ ] `documentation-research`
   - [ ] `pattern-detection`

2. **Rewrite top 10 most-used skill descriptions**
   - [ ] `prd-management` - Add trigger phrases
   - [ ] `parallel-agents` - Simplify and add phrases
   - [ ] `mcp-security` - Add trigger phrases
   - [ ] `django-dev` - Add trigger phrases (or mark knowledge-only)
   - [ ] `python-code-review` - Add trigger phrases
   - [ ] `typescript-code-review` - Add trigger phrases

### Medium Priority

3. **Audit all skills for user-invocable status**
   - Review each skill's SKILL.md
   - Ask: "Would a user explicitly request this, or should it auto-apply?"
   - Mark knowledge/pattern skills as `user-invocable: false`

4. **Add `disable-model-invocation: true` where needed**
   - Deployment operations
   - Database migrations
   - Any destructive operations

### Low Priority

5. **Reduce SKILL.md file sizes**
   - Split files over 500 lines
   - Move examples to separate files
   - Use progressive disclosure

6. **Test trigger phrases**
   - Ask sample users how they'd request each skill
   - Update descriptions based on real usage patterns

## Description Formula

Use this template for action skills:

```yaml
description: Use when [phrase 1], [phrase 2], [phrase 3], [phrase 4], or [phrase 5]. [One sentence about what it does/provides].
```

**Example**:
```yaml
description: Use when creating PRDs, organizing requirements, tracking product specs, updating document status, or archiving completed features. Auto-applies naming conventions and lifecycle management.
```

## Testing Your Improvements

After updating descriptions, test with these questions:

1. **Natural language test**: Would a user actually say these phrases?
   - ✅ "help me organize my PRD"
   - ❌ "initialize PRD lifecycle management subsystem"

2. **Specificity test**: Are the phrases specific enough to match this skill?
   - ✅ "prevent prompt injection in my MCP server"
   - ❌ "make it secure" (too vague)

3. **Diversity test**: Do the phrases cover different ways of asking?
   - ✅ "test this feature", "design test cases", "write QA tests"
   - ❌ "test this feature", "test that feature" (too similar)

## Examples: Before & After

### Example 1: Product Strategy

**Before**:
```yaml
description: Chief Product Officer expertise with proven frameworks and strategic guidance. Use when discussing product vision, conducting discovery, validating market fit, planning roadmaps, or making build-vs-buy decisions.
```

**After**:
```yaml
description: Use when planning product strategy, defining product vision, validating market fit, prioritizing features, creating roadmaps, or making build-vs-buy decisions. Provides CPO-level frameworks and strategic guidance.
```

**Why better**: Moved action phrases to front, simplified language, removed title/role focus.

### Example 2: Network Inspection

**Before**:
```yaml
description: HTTP request and response analysis for debugging API calls, identifying failed requests, and inspecting network traffic.
```

**After**:
```yaml
description: Use when debugging API calls, checking network requests, inspecting HTTP traffic, finding failed requests, or analyzing response data. Provides detailed request/response analysis tools.
```

**Why better**: Added explicit trigger phrases users would say.

### Example 3: Console Debugging

**Before**:
```yaml
description: Browser console message analysis for debugging JavaScript errors, warnings, and application logs.
```

**After**:
```yaml
description: Use when debugging JavaScript errors, checking console warnings, analyzing browser logs, finding runtime errors, or investigating console output. Provides console message analysis and filtering.
```

**Why better**: More varied phrases covering different ways users ask for help.

## Sources

Research for this analysis:

- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Agent Skills - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Build Your First Claude Code Agent Skill](https://medium.com/@richardhightower/build-your-first-claude-code-skill-a-simple-project-memory-system-that-saves-hours-1d13f21aff9e)
- [Claude Skills and CLAUDE.md: a practical 2026 guide](https://www.gend.co/blog/claude-skills-claude-md-guide)
- [Claude Agent Skills Landing Guide](https://claudecn.com/en/blog/claude-agent-skills-landing-guide/)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## Next Steps

1. Review this analysis
2. Prioritize which skills to update first (suggest top 10 most-used)
3. Create a batch of updated SKILL.md files
4. Test with real usage patterns
5. Run `/forge-refresh --force` to redeploy
6. Monitor which skills get invoked more frequently
7. Iterate based on usage data
