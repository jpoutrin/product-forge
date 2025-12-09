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

**Return a JSON design document:**
```json
{
  "output_dir": "{parallel_dir}",
  "manifest": { ... },
  "tasks": [
    {
      "id": "task-001",
      "component": "users",
      "wave": 1,
      "agent": "python-experts:django-expert",
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
| Agent 4 | `tasks/*.md` (all task files) |
| Agent 5 | `prompts/*.txt` (all prompt files) |

Each agent receives the relevant section from Phase 1's JSON output.

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
- For manifest.json: invoke `parallel-agents` skill
- For prompt files (prompts/*.txt): invoke `parallel-prompt-generator` skill
  - **IMPORTANT**: The prompt template in this skill includes mandatory sections:
    - `=== EXECUTION INSTRUCTIONS ===`
    - `=== IMPORTANT RULES ===`
    - `=== OUTPUT FORMAT (REQUIRED) ===` with JSON block
    - `=== COMPLETION SIGNAL ===`
  - You MUST include ALL sections from the skill template in every generated prompt

Write all files now using the exact templates from the skills. Do not ask for confirmation.
~~~

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
| `/parallel-run` | Execute parallel agents via cpo |
| `/parallel-integrate` | Post-execution verification |
| `/create-tech-spec` | Create Tech Spec before decomposition |
