# Skills Improvement Action Plan

## TL;DR - Do This First

1. **Add `user-invocable: false` to 9 knowledge skills** (10 minutes)
2. **Rewrite 5 most critical skill descriptions** (15 minutes)
3. **Run `/forge-refresh --force`** (1 minute)
4. **Test with real questions** (5 minutes)

**Total time: ~30 minutes for massive improvement**

---

## Phase 1: Knowledge Skills (HIGHEST IMPACT)

**Why**: These skills should auto-load when relevant, not require explicit request. Adding `user-invocable: false` immediately improves their effectiveness.

**Time**: 10 minutes

### Files to Edit:

1. `plugins/devops-data/skills/mcp-architecture/SKILL.md`
2. `plugins/python-experts/skills/django-dev/SKILL.md`
3. `plugins/python-experts/skills/python-style/SKILL.md`
4. `plugins/frontend-experts/skills/typescript-style/SKILL.md`
5. `plugins/product-design/skills/qa-testing-methodology/SKILL.md`
6. `plugins/python-experts/skills/documentation-research/SKILL.md`
7. `plugins/claude-code-dev/skills/pattern-detection/SKILL.md`
8. `plugins/python-experts/skills/python-code-review/SKILL.md`
9. `plugins/frontend-experts/skills/typescript-code-review/SKILL.md`

### What to Change:

Add this line to the frontmatter of each file:
```yaml
user-invocable: false
```

**Example** (mcp-architecture):
```yaml
---
name: mcp-architecture
description: MCP architecture patterns, security, and memory management. Auto-loads when building MCP servers, implementing tools/resources, discussing MCP security, or working with FastMCP.
user-invocable: false  # ← ADD THIS LINE
---
```

---

## Phase 2: Critical Action Skills (HIGH IMPACT)

**Why**: These are frequently used skills with poor descriptions. Improving them will show immediate results.

**Time**: 15 minutes

### Top 5 Skills to Rewrite:

#### 1. prd-management ⭐ MOST USED
**File**: `plugins/product-design/skills/prd-management/SKILL.md`

**Replace**:
```yaml
description: Automatic PRD lifecycle management, organization, and status tracking. Use when working with Product Requirements Documents (PRDs) or Feature Requirements Documents (FRDs) for proper naming, directory structure, and status transitions.
```

**With**:
```yaml
description: Use when organizing PRDs, tracking requirements, managing product specs, updating PRD status, archiving completed docs, or setting up PRD structure. Auto-applies naming conventions and lifecycle management.
```

#### 2. parallel-agents ⭐ HIGH VALUE
**File**: `plugins/product-design/skills/parallel-agents/SKILL.md`

**Replace**:
```yaml
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
when: User wants to parallelize development, run multiple agents simultaneously, decompose a PRD into independent tasks, scale work across concurrent workstreams, or coordinate multi-agent workflows
```

**With**:
```yaml
description: Use when parallelizing development, running multiple agents, splitting work across agents, coordinating parallel tasks, or decomposing PRDs for concurrent execution. Breaks work into independent agent workstreams.
```

**Also remove the `when:` field** (redundant).

#### 3. mcp-security ⭐ SECURITY-CRITICAL
**File**: `plugins/security-compliance/skills/mcp-security/SKILL.md`

**Replace**:
```yaml
description: Multi-agent and MCP pipeline security with 5-layer defense architecture. Use when building MCP servers, multi-agent systems, or any pipeline that handles user input to prevent prompt injection and ensure proper authorization.
```

**With**:
```yaml
description: Use when securing MCP servers, preventing prompt injection, implementing authorization, validating user input, or building secure multi-agent pipelines. Provides 5-layer defense architecture patterns.
```

#### 4. network-inspection
**File**: `plugins/product-design/skills/network-inspection/SKILL.md`

**Replace**:
```yaml
description: HTTP request and response analysis for debugging API calls, identifying failed requests, and inspecting network traffic.
```

**With**:
```yaml
description: Use when debugging API calls, checking network requests, inspecting HTTP traffic, finding failed requests, analyzing response data, or investigating API errors. Provides detailed request/response analysis.
```

#### 5. console-debugging
**File**: `plugins/product-design/skills/console-debugging/SKILL.md`

**Replace**:
```yaml
description: Browser console message analysis for debugging JavaScript errors, warnings, and application logs.
```

**With**:
```yaml
description: Use when debugging JavaScript errors, checking console warnings, analyzing browser logs, finding runtime errors, investigating console output, or troubleshooting browser issues. Provides console message analysis.
```

---

## Phase 3: Deploy & Test

### Step 1: Deploy Changes
```bash
/forge-refresh --force
```

### Step 2: Test Knowledge Skills (Should Auto-Load)

Try these tasks - skills should auto-invoke WITHOUT you mentioning them:

1. **Django** - "Create a Django model for User" → `django` should auto-load
2. **MCP Architecture** - "Help me build an MCP server" → `mcp-architecture` should auto-load
3. **Python Style** - "Write a Python function" → `python-style` should auto-load
4. **QA Methodology** - "Design test cases for login" → `qa-testing-methodology` should auto-load

### Step 3: Test Action Skills (User Phrases)

Try these user questions - skills should invoke:

1. **PRD Management**:
   - "Help me organize my PRD"
   - "Track my product requirements"
   - "Update PRD status"

2. **Parallel Agents**:
   - "Run multiple agents on this"
   - "Split this work across agents"
   - "Parallelize this development"

3. **MCP Security**:
   - "Secure my MCP server"
   - "Prevent prompt injection"
   - "Add authorization"

4. **Network Inspection**:
   - "Debug this API call"
   - "Check the network request"
   - "Find failed requests"

5. **Console Debugging**:
   - "Check console errors"
   - "Debug JavaScript warnings"
   - "Investigate browser logs"

---

## Success Metrics

After Phase 1-3 (30 minutes of work), you should see:

✅ **Knowledge skills auto-load** when working with relevant code
✅ **Action skills trigger** from natural user questions
✅ **Fewer explicit skill invocations** needed (Claude picks the right skill)
✅ **Better context awareness** (skills load proactively)

---

## Phase 4: Remaining Skills (MEDIUM PRIORITY)

**When**: After Phase 1-3 proves successful

**Time**: 1-2 hours

### Skills to Update:

These follow the same pattern - see `skills-rewrites-ready-to-apply.md` for exact changes:

- `qa-test-management`
- `product-strategy`
- `design-system`
- `parallel-task-format`
- `task-orchestration`
- `parallel-decompose`
- All `devops-data` skills
- All `rag-cag` skills

---

## Phase 5: Full Audit (LOW PRIORITY)

**When**: After 1 week of monitoring Phase 1-4

**Time**: 3-4 hours

1. Review all 80+ skills systematically
2. Categorize each as:
   - ✅ Knowledge skill (needs `user-invocable: false`)
   - ✅ Action skill (needs trigger phrases)
   - ✅ Command skill (already good)
3. Apply pattern consistently
4. Test and iterate

---

## Quick Reference: The Pattern

### For Knowledge Skills:
```yaml
---
name: skill-name
description: [What it provides]. Auto-loads when [relevant context]. [Key features].
user-invocable: false
---
```

### For Action Skills:
```yaml
---
name: skill-name
description: Use when [phrase 1], [phrase 2], [phrase 3], [phrase 4], or [phrase 5]. [What it does in one sentence].
---
```

---

## Common Pitfalls to Avoid

❌ **Don't**: "Comprehensive PRD lifecycle management system"
✅ **Do**: "Use when organizing PRDs, tracking requirements, managing specs"

❌ **Don't**: "Use when initiating comprehensive test coverage subsystem"
✅ **Do**: "Use when designing test cases, planning QA tests, ensuring coverage"

❌ **Don't**: "Multi-agent orchestration framework for parallel development"
✅ **Do**: "Use when parallelizing development, running multiple agents, splitting work"

---

## ROI Estimate

**Time invested**: 30 minutes (Phase 1-3)
**Expected improvement**:
- 30-50% better skill auto-invocation
- 40-60% fewer cases where Claude picks wrong skill
- Better user experience (Claude "just knows" what to do)

**Time invested**: 2 hours (Phase 1-4)
**Expected improvement**:
- 50-70% better skill matching overall
- Significantly reduced need for explicit `/skill-name` invocations
- More proactive, context-aware Claude behavior

---

## Next Steps

1. ✅ Read this action plan
2. ⬜ Execute Phase 1 (10 min) - Add `user-invocable: false`
3. ⬜ Execute Phase 2 (15 min) - Rewrite top 5 descriptions
4. ⬜ Execute Phase 3 (5 min) - Deploy & test
5. ⬜ Monitor for 2-3 days
6. ⬜ Review results
7. ⬜ Execute Phase 4 if Phase 1-3 successful

---

## Questions?

- See `skills-matching-analysis.md` for full research and rationale
- See `skills-rewrites-ready-to-apply.md` for all 20+ specific rewrites
- Run `/forge-help` to see all available skills after deployment
