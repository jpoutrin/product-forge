# `when:` Field Analysis

## How It's Used

The indexer script (`generate-forge-index.py`) extracts the `when:` field and displays it in the generated index:

```python
# Lines 88, 111, 134, 182 - Extract from frontmatter
"when": meta.get("when", ""),

# Lines 219, 248, 278, 309 - Display in markdown
if s["when"]:
    lines.append(f"  - _When: {s['when']}_")
```

**Purpose**: Provides additional context in the forge-index.md documentation about when to use a skill/agent/command.

---

## The Problem: Redundancy

Many skills have redundant information between `description` and `when:` fields:

### Example 1: zod
```yaml
description: Apply Zod patterns when writing schema validation, data parsing, or type-safe validation in TypeScript. Use for API input validation, form validation, configuration parsing, and runtime type checking.
when: User needs schema validation, data parsing, form validation, or runtime type checking in TypeScript
```
**Issue**: The `when:` field just repeats what's already in the description.

### Example 2: fastmcp
```yaml
description: Build MCP servers using the FastMCP TypeScript framework. Use when creating tools, resources, prompts, implementing authentication, session management, or configuring transports for Model Context Protocol servers.
when: User creates MCP servers, implements MCP tools/resources/prompts, or works with FastMCP framework
```
**Issue**: The `when:` field is a subset of what's in the description.

---

## Key Insight: Two Different Audiences

1. **`description`** → Used by Claude's LLM for skill matching (most important)
2. **`when:`** → Used by humans reading forge-index.md (documentation)

Both are valuable, but they serve different purposes:
- **Description** needs natural trigger phrases for Claude to match
- **`when:`** can be more concise/technical for human reference

---

## Recommended Strategy

### Option A: Keep Both, Make Them Complementary

**Description** = Natural language for Claude matching (with trigger phrases)
**When** = Concise, technical summary for documentation

**Example (zod)**:
```yaml
description: Zod schema validation patterns and type inference. Auto-loads when validating schemas, parsing data, validating forms, checking types at runtime, or using z.object/z.string/z.infer in TypeScript.
when: Working with Zod schemas, runtime validation, or type-safe parsing
user-invocable: false
```

**Example (fastmcp)**:
```yaml
description: FastMCP TypeScript framework patterns for MCP servers. Auto-loads when building MCP servers, creating tools/resources/prompts, implementing authentication, configuring transports, or working with FastMCP in TypeScript.
when: Building MCP servers with FastMCP framework
user-invocable: false
```

### Option B: Remove `when:` If Redundant

If the `when:` field doesn't add value beyond the description, just omit it.

**Example**:
```yaml
description: Zod schema validation patterns and type inference. Auto-loads when validating schemas, parsing data, validating forms, checking types at runtime, or using z.object/z.string/z.infer in TypeScript.
user-invocable: false
# No when: field - description is sufficient
```

---

## Revised Recommendations

### For Skills with Redundant `when:` Fields

#### 1. zod

**Current**:
```yaml
description: Apply Zod patterns when writing schema validation, data parsing, or type-safe validation in TypeScript. Use for API input validation, form validation, configuration parsing, and runtime type checking.
when: User needs schema validation, data parsing, form validation, or runtime type checking in TypeScript
```

**Recommended Option A** (Keep both, make complementary):
```yaml
description: Zod schema validation patterns and type inference. Auto-loads when validating schemas, parsing data, validating forms, checking types at runtime, or using z.object/z.string/z.infer in TypeScript.
when: Working with Zod schemas or runtime type validation
user-invocable: false
```

**Recommended Option B** (Remove redundant when):
```yaml
description: Zod schema validation patterns and type inference. Auto-loads when validating schemas, parsing data, validating forms, checking types at runtime, or using z.object/z.string/z.infer in TypeScript.
user-invocable: false
```

---

#### 2. fastmcp

**Current**:
```yaml
description: Build MCP servers using the FastMCP TypeScript framework. Use when creating tools, resources, prompts, implementing authentication, session management, or configuring transports for Model Context Protocol servers.
when: User creates MCP servers, implements MCP tools/resources/prompts, or works with FastMCP framework
```

**Recommended Option A** (Keep both, make complementary):
```yaml
description: FastMCP TypeScript framework patterns for MCP servers. Auto-loads when building MCP servers, creating tools/resources/prompts, implementing authentication, configuring transports, or working with FastMCP in TypeScript.
when: Building MCP servers with FastMCP
user-invocable: false
```

**Recommended Option B** (Remove redundant when):
```yaml
description: FastMCP TypeScript framework patterns for MCP servers. Auto-loads when building MCP servers, creating tools/resources/prompts, implementing authentication, configuring transports, or working with FastMCP in TypeScript.
user-invocable: false
```

---

#### 3. typescript-import-style

**Current**:
```yaml
description: Apply import formatting and ordering rules that minimize merge conflicts when multiple developers or parallel agents modify the same file. Enforces one-import-per-line, alphabetical sorting, and consistent grouping.
when: Writing TypeScript/JavaScript code with imports, especially in multi-agent parallel development or team environments
```

**Recommended Option A** (Keep both, make complementary):
```yaml
description: Merge-friendly import formatting (one-per-line, alphabetical). Auto-loads when writing TypeScript/JavaScript imports to minimize merge conflicts in parallel development. Enforces consistent grouping and sorting.
when: Writing TypeScript imports in multi-agent environments
user-invocable: false
```

**Recommended Option B** (Remove redundant when):
```yaml
description: Merge-friendly import formatting (one-per-line, alphabetical). Auto-loads when writing TypeScript/JavaScript imports to minimize merge conflicts in parallel development. Enforces consistent grouping and sorting.
user-invocable: false
```

---

## Guidelines for `when:` Field Usage

### When to KEEP the `when:` field:
✅ It provides concise summary distinct from description
✅ It helps humans quickly understand the use case
✅ The description has many trigger phrases but when: is short

### When to REMOVE the `when:` field:
❌ It just repeats what's in the description
❌ It doesn't add any new information
❌ The description is already concise enough

---

## Pattern Analysis Across All Skills

Let me check how `when:` is used across all skills to find patterns:

```bash
# Count skills with when: field
grep -r "^when:" plugins/*/skills/*/SKILL.md | wc -l
```

### Good Example of Complementary Usage:

**parallel-agents** (before our changes):
```yaml
description: Orchestrate parallel development with multiple Claude Code agents from PRD specs. Use when asked to parallelize development, break down a PRD into agent tasks, coordinate multi-agent workflows, or scale development across independent workstreams.
when: User wants to parallelize development, run multiple agents simultaneously, decompose a PRD into independent tasks, scale work across concurrent workstreams, or coordinate multi-agent workflows
```
**Issue**: Almost identical - pure redundancy

**Better**:
```yaml
description: Use when parallelizing development, running multiple agents, splitting work across agents, coordinating parallel tasks, or decomposing PRDs for concurrent execution. Breaks work into independent agent workstreams.
when: Multi-agent parallel development from PRDs
```

---

## Recommendation for Product Forge

### Short-term: Option A (Keep Both, Make Complementary)

For skills where `when:` is redundant, revise it to be concise and complementary:

1. **Description**: Natural trigger phrases for Claude (detailed)
2. **When**: Brief, technical summary for humans (1 line)

**Benefits**:
- Maintains compatibility with indexer
- Improves forge-index.md readability
- Better skill matching via descriptions

### Long-term: Consider Indexer Enhancement

The indexer could be improved to auto-generate concise `when:` summaries from descriptions using AI, so authors only need to write one good description.

---

## My Recommendation

Use **Option A** - keep both fields but make them complementary:

1. **Description**: Optimize for Claude's LLM matching (natural trigger phrases)
2. **When**: Keep as a concise human-readable summary (5-10 words)

This provides:
- ✅ Better skill matching (from improved descriptions)
- ✅ Better documentation (from concise when: fields)
- ✅ No breaking changes to indexer
- ✅ Clear separation of concerns

---

## Action Items

1. ✅ Update descriptions with natural trigger phrases
2. ✅ Add `user-invocable: false` to knowledge skills
3. ✅ Revise `when:` fields to be concise summaries (not redundant)
4. ⏭️ Consider: AI-powered indexer that auto-generates `when:` from descriptions
