---
description: Decompose PRD into parallel tasks with contracts and prompts
argument-hint: <tech-spec-file> [--prd <prd-file>] [--name <slug>] [--tech django|typescript|go]
---

# parallel-decompose

**Category**: Parallel Development

## Usage

```bash
/parallel-decompose <tech-spec-file> [--prd <prd-file>] [--tech django|typescript|go]
/parallel-decompose --name <slug> [--prd <prd-file>] [--tech django|typescript|go]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<tech-spec-file>` | Yes* | Path to Tech Spec (determines folder: `TS-XXXX-slug`) |
| `--prd` | No | Path to PRD or FRD file for additional context |
| `--name` | Fallback* | Manual slug if no Tech Spec (creates `parallel/{slug}/`) |
| `--tech` | No | Technology stack (default: auto-detect) |

*Either `<tech-spec-file>` or `--name` is required.

## Purpose

Decompose a Tech Spec into independent, parallel-executable task specifications:

1. Creates `parallel/TS-XXXX-slug/` directory
2. Generates contracts, tasks, and prompts
3. Creates manifest.json for `cpo` execution

## Execution Instructions for Claude Code

When this command is run with arguments, Claude Code should:

1. **Parse arguments from the command invocation:**
   - First positional argument is the Tech Spec file path (primary input)
   - `--prd <path>` optionally provides a PRD/FRD for additional context
   - `--name <slug>` provides a manual slug (fallback if no Tech Spec)
   - `--tech <stack>` provides the technology hint (django, typescript, go)

2. **Validate inputs:**
   - Require either Tech Spec file (positional) or `--name` (error if neither)
   - Verify Tech Spec file exists (if provided)
   - If `--prd` provided, verify PRD file exists
   - Tech Spec contains implementation details; PRD provides business context

3. **Determine output directory:**
   - With Tech Spec: Extract TS-XXXX ID and slug → `parallel/TS-XXXX-slug/`
   - With `--name`: Use provided slug → `parallel/{slug}/`

4. **Execute two-phase decomposition** (see Execution Method below)

5. **Report results** with task count, wave count, and next steps

## Prerequisites

- Run `/parallel-setup` once (creates `parallel/` root directory)
- Tech Spec provides implementation details, design decisions, and contracts
- PRD optional but useful for business context and requirements validation

## Execution Method

This command uses a **two-phase approach** for optimal quality and speed:

### Phase 1: Analysis & Design (Opus)

Spawn `cto-architect` agent for high-quality architectural decisions:

```
Use the Task tool with:
- subagent_type: devops-data:cto-architect
- model: opus (inherited from agent definition)
```

**Phase 1 Prompt:**

~~~
You are analyzing a Tech Spec to design a parallel task decomposition.

**Inputs:**
- Tech Spec: {tech_spec_path}
- PRD: {prd_file_path} (or "not provided" - for business context only)
- Technology: {tech_stack}
- Output Directory: {parallel_dir}

**Your task (ANALYSIS ONLY - do not write files yet):**
1. Read the Tech Spec (primary source for implementation details)
2. If PRD provided, review for business context and requirements
3. Identify logical components and their boundaries
4. Design wave structure and dependencies
5. Define contract interfaces (types and API schemas)
6. Assign appropriate agents to each task
7. Identify ALL dependencies required by tasks:
   - Analyze imports in Tech Spec code examples
   - Include test dependencies (pytest, pytest-asyncio, etc.)
   - Aggregate unique dependencies across all tasks
   - Separate into: add (new), upgrade (existing), add_dev (dev-only)
8. Align dependency versions (invoke `dependency-alignment` skill):
   - Detect project ecosystem (Python/Node.js) from project files
   - For Python: Use `uv pip compile --dry-run` to resolve each dependency
   - For Node.js: Use `npm view <pkg>@"<range>" version --json`
   - Resolve to pinned versions compatible with existing project dependencies
   - Auto-resolve conflicts to compatible versions
   - Output pinned versions (e.g., `pydantic==2.5.3`, `zod@3.22.4`)
9. Resolve skills for each task:
   - Reference `parallel-agents/agent-skills-mapping.yaml`
   - Look up the agent assigned to each task
   - Include the skills list in the task specification

**Return a JSON design document:**
```json
{
  "output_dir": "{parallel_dir}",
  "manifest": {
    "dependencies": {
      "python": {
        "add": ["pydantic==2.5.3", "sqlalchemy==2.0.25"],
        "upgrade": [],
        "remove": [],
        "add_dev": ["pytest==7.4.3", "pytest-asyncio==0.21.1"]
      }
    }
  },
  "tasks": [
    {
      "id": "task-001",
      "component": "users",
      "wave": 1,
      "agent": "python-experts:django-expert",
      "skills": ["python-experts:python-style", "python-experts:django-dev", "python-experts:django-api", "python-experts:documentation-research"],
      "scope": { "create": [...], "modify": [...], "boundary": [...] },
      "requirements": [...],
      "checklist": [...]
    }
  ],
  "contracts": {
    "types": "... Python/TypeScript code ...",
    "api_schema": "... OpenAPI YAML ..."
  },
  "architecture_summary": "...",
  "context_summary": "..."
}
```
~~~

### Phase 2: File Generation (Sonnet)

Spawn Sonnet agents in parallel to write files efficiently:

```
Use the Task tool with:
- subagent_type: general-purpose
- model: sonnet
```

**Parallel Sonnet agents:**

| Agent | Writes |
|-------|--------|
| Agent 1 | `manifest.json`, `context.md` |
| Agent 2 | `contracts/types.py`, `contracts/api-schema.yaml` |
| Agent 3 | `architecture.md`, `task-graph.md` |
| Agent 4 | `tasks/*.md` (all task files, including `skills` in YAML frontmatter) |
| Agent 5 | `prompts/*.txt` (all prompt files, with `=== REQUIRED SKILLS ===` section) |

Each agent receives the relevant section from Phase 1's JSON output.

**IMPORTANT - Skills placement:**
- `skills` are written to **task files** (tasks/*.md) by Agent 4 in YAML frontmatter
- `skills` are written to **prompt files** (prompts/*.txt) by Agent 5 in `=== REQUIRED SKILLS ===` section
- `skills` are **NOT** written to manifest.json - manifest only contains `id` and `agent` per task

**Phase 2 Prompt Template (per agent):**

~~~
Write the following files based on this design specification.

**Output Directory:** {parallel_dir}
**Files to write:** {file_list}

**Design specification:**
{relevant_section_from_phase1}

**CRITICAL - Before writing any files:**
1. Invoke the Skill tool to load the format specification
2. Read the skill's template section completely
3. Use the EXACT template format from the skill

**Required skill invocations by file type:**
- For task files (tasks/*.md): invoke `parallel-task-format` skill
  - **Include `skills` in YAML frontmatter** - list of skills the agent needs to invoke
- For manifest.json: invoke `parallel-agents` skill
  - **DO NOT include `skills` in manifest.json** - only `id` and `agent` per task
- For prompt files (prompts/*.txt): invoke `parallel-prompt-generator` skill
  - **IMPORTANT**: The prompt template in this skill includes mandatory sections:
    - `=== EXECUTION INSTRUCTIONS ===`
    - `=== IMPORTANT RULES ===` (includes CONTRACTS ARE DESIGN DOCUMENTS directive)
    - `=== REQUIRED SKILLS ===` (list of skills the agent must invoke)
    - `=== COMPLETION SIGNAL ===`
  - You MUST include ALL sections from the skill template in every generated prompt

**FOR PROMPT GENERATION (Agent 5) - VERBATIM COPY REQUIREMENTS:**
1. Read `context.md` completely - include ALL content in === CONTEXT === section (do not summarize)
2. For each task file in `tasks/`:
   a. Parse YAML frontmatter (id, agent, wave, deps, contracts, **skills**)
   b. Extract Scope section (CREATE, MODIFY, BOUNDARY) - copy exactly
   c. Extract Requirements section - COPY EVERY bullet point EXACTLY as written
   d. Extract Checklist section - COPY EVERY item EXACTLY as written
3. Match exact field names from contracts (e.g., use `principal_id` not `user_id`)
4. Include the CONTRACTS DESIGN DOCUMENTS directive from the skill template
5. Include === REQUIRED SKILLS === section in every prompt:
   - Get skills from the task file's `skills` field in YAML frontmatter
   - List each skill as a bullet: `- plugin:skill-name`
   - Include invocation syntax: `skill: "plugin:skill-name"`

**DO NOT (for prompt generation):**
- Summarize or paraphrase requirements
- Change field names or types
- Omit any checklist items
- Shorten the context

Write all files now using the exact templates from the skills. Do not ask for confirmation.
~~~

**Post-Generation Validation (by main agent):**

After Phase 2 agents complete, verify each generated prompt:
- [ ] `=== REQUIRED SKILLS ===` section present with skills list
- [ ] Requirements in prompt match task file exactly (field names, types)
- [ ] All checklist items from task appear in prompt
- [ ] Full context.md is included (line count should match)
- [ ] CONTRACTS DESIGN DOCUMENTS directive present in IMPORTANT RULES
- [ ] No references to importing from parallel/ directory

### Why Two Phases?

| Phase | Model | Rationale |
|-------|-------|-----------|
| Analysis & Design | Opus | Complex reasoning for dependencies, boundaries, agent selection |
| File Generation | Sonnet | Fast, efficient templated output |

This approach provides Opus-quality decomposition at Sonnet-level cost for file generation.

## Output Directory Logic

**If Tech Spec provided (positional argument)**:
1. Extract `tech_spec_id` (e.g., `TS-0042`) and slug from Tech Spec
2. Output to: `parallel/TS-0042-inventory-system/`

**If `--name` provided (fallback)**:
1. Output to: `parallel/{slug}/`

**If neither**: Error - must provide Tech Spec file or `--name`

## Output Structure

```
parallel/TS-0042-inventory-system/
  manifest.json           # cpo execution manifest
  context.md              # Shared project context
  architecture.md         # System design + Mermaid diagram
  task-graph.md           # Dependency visualization
  contracts/
    types.py              # Shared domain types
    api-schema.yaml       # OpenAPI specification
  tasks/
    task-001-users.md     # Compact YAML format
    task-002-products.md
    ...
  prompts/
    agent-prompts.md      # Wave summary + launch commands
    task-001.txt          # Individual agent prompts
    task-002.txt
    ...
```

## manifest.json Format

Uses `cpo` format (see `parallel-agents` skill for details):

```json
{
  "tech_spec_id": "TS-0042",
  "name": "inventory-system",
  "technology": "python",
  "python_version": "3.11",
  "dependencies": {
    "python": {
      "add": ["pydantic>=2.0", "sqlalchemy[asyncio]>=2.0"],
      "upgrade": [],
      "remove": [],
      "add_dev": ["pytest>=7.0", "pytest-asyncio>=0.21"]
    }
  },
  "waves": [
    {
      "number": 1,
      "tasks": [
        { "id": "task-001", "agent": "python-experts:django-expert" },
        { "id": "task-002", "agent": "python-experts:django-expert" }
      ],
      "validation": "from apps.users.models import User; print('Wave 1 OK')"
    }
  ],
  "metadata": {
    "tech_spec": "tech-specs/approved/TS-0042-inventory.md",
    "generated_at": "2025-01-15T10:00:00Z",
    "total_tasks": 3,
    "max_parallel": 2,
    "critical_path": ["task-001", "task-003"]
  }
}
```

**Note:** `skills` are intentionally NOT in manifest.json. The manifest is for `cpo` orchestration only. Skills are stored in:
- Task files (`tasks/*.md`) - YAML frontmatter `skills` field
- Prompt files (`prompts/*.txt`) - `=== REQUIRED SKILLS ===` section

### Dependencies Section

The `dependencies` section is installed before any task execution begins:

| Field | Description |
|-------|-------------|
| `python.add` | Packages to add (if not present) |
| `python.upgrade` | Packages to upgrade to specified version |
| `python.remove` | Packages to remove from project |
| `python.add_dev` | Dev-only packages to add |

Operations execute in order: remove → upgrade → add → add_dev. Changes are committed to the feature branch before task execution starts.

## Example

```bash
# Tech Spec only (most common)
/parallel-decompose tech-specs/approved/TS-0042-inventory.md

# Tech Spec with technology hint
/parallel-decompose tech-specs/approved/TS-0042-inventory.md --tech django

# Tech Spec with PRD for additional context
/parallel-decompose tech-specs/approved/TS-0042-inventory.md --prd docs/inventory-prd.md

# Without Tech Spec (fallback using --name)
/parallel-decompose --name user-auth --prd docs/auth-frd.md --tech django
```

## Expected Output

```
Decomposition Complete

Output: parallel/TS-0042-inventory-system/
Tech Spec: TS-0042
PRD: docs/inventory-prd.md (optional)

Tasks: 6
Waves: 3
Max parallel: 3

Next: Run `cpo run parallel/TS-0042-inventory-system/` to execute
```

## Related Skills

| Skill | Use For |
|-------|---------|
| `parallel-decompose` | Full decomposition workflow details |
| `parallel-task-format` | Task YAML format, scope notation |
| `parallel-prompt-generator` | Prompt task format to feed the cpo tool with |
| `parallel-agents` | manifest.json format, directory structure |
| `agent-tools` | Tool permissions for agents |

## Related Commands

| Command | Purpose |
|---------|---------|
| `/parallel-setup` | One-time project initialization |
| `/parallel-validate-prompts` | Validate prompts have required sections |
| `/parallel-run` | Execute parallel agents via cpo |
| `/parallel-integrate` | Post-execution verification |
| `/create-tech-spec` | Create Tech Spec before decomposition |
