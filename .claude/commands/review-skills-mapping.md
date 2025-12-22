---
description: Review skills and validate agent-skills-mapping.yaml compatibility
argument-hint: "[--fix] [--verbose]"
keywords: skills, mapping, agents, validate, review, compatibility
---

# review-skills-mapping

**Category**: Plugin Development

## Usage

```bash
/review-skills-mapping [--fix] [--verbose]
```

## Options

| Option | Description |
|--------|-------------|
| `--fix` | Auto-fix issues (add missing skills to mapping, remove invalid references) |
| `--verbose` | Show detailed information for each skill |

## Purpose

Reviews all skills across Product Forge plugins and validates compatibility with `agent-skills-mapping.yaml`. Use this command to:

- Verify all skills referenced in mapping actually exist
- Find skills not included in any agent's mapping
- Detect skills with invalid structure (missing SKILL.md, bad frontmatter)
- Ensure agent-skills-mapping.yaml stays in sync with available skills

## What Gets Checked

### 1. Skills Inventory

Scans all plugins for skills:
```
plugins/*/skills/*/SKILL.md
```

### 2. Mapping Validation

Cross-references `agent-skills-mapping.yaml` to verify:
- All referenced skills exist
- Skill names use correct format (`plugin:skill-name`)
- No duplicate skills in agent lists

### 3. Coverage Analysis

Identifies:
- Skills not mapped to any agent (orphaned)
- Agents with empty skill lists
- Skills that could be suggested for agents based on plugin affinity

---

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Parse Arguments

```
FIX_MODE = true if --fix specified
VERBOSE = true if --verbose specified
```

### 2. Inventory All Skills

Scan for all SKILL.md files:

```bash
find plugins -path "*/skills/*/SKILL.md" -type f
```

For each skill, extract:
- Plugin name (from path)
- Skill name (from directory name)
- Full qualified name: `{plugin}:{skill-name}`
- Frontmatter fields (name, description, when)

### 3. Load Agent-Skills Mapping

Read the mapping file:
```
plugins/product-design/skills/parallel-agents/agent-skills-mapping.yaml
```

Parse all agents and their skill lists.

### 4. Cross-Reference Validation

#### Check 1: Referenced Skills Exist

For each skill in mapping, verify the SKILL.md exists:

```python
for agent, config in mapping['agents'].items():
    for skill in config.get('skills', []):
        plugin, skill_name = skill.split(':')
        path = f"plugins/{plugin}/skills/{skill_name}/SKILL.md"
        if not exists(path):
            report_error(f"Missing skill: {skill} (referenced by {agent})")
```

#### Check 2: Orphaned Skills

Find skills not mapped to any agent:

```python
all_mapped_skills = set()
for agent, config in mapping['agents'].items():
    all_mapped_skills.update(config.get('skills', []))

for skill in discovered_skills:
    if skill not in all_mapped_skills:
        report_warning(f"Orphaned skill: {skill} (not mapped to any agent)")
```

#### Check 3: Skill Structure Validation

For each skill, verify:
- SKILL.md has valid YAML frontmatter
- `name` field matches directory name
- `description` field is present

### 5. Report Results

#### Default Output

```
Skills Mapping Review
=====================

Source: plugins/product-design/skills/parallel-agents/agent-skills-mapping.yaml

Inventory:
  Total skills discovered: 25
  Skills in mapping: 18
  Orphaned skills: 7

Validation Results:
  ✅ All referenced skills exist
  ⚠️  7 orphaned skills (not mapped to any agent)

Orphaned Skills:
  - product-design:console-debugging
  - product-design:network-inspection
  - product-design:qa-element-extraction
  - product-design:qa-screenshot-management
  - product-design:qa-screenshot-validation
  - devops-data:portman
  - devops-data:direnv

Agents with Empty Skills:
  - devops-data:cto-architect (intentional - uses judgment)

Suggestions:
  Consider adding these skills to relevant agents:
  - product-design:qa-tester could use: qa-element-extraction, qa-screenshot-management
  - devops-data:devops-expert could use: portman, direnv

Run with --fix to update the mapping file.
```

#### Verbose Output (--verbose)

```
Skills Mapping Review
=====================

=== Skill Inventory ===

product-design:parallel-agents
  Path: plugins/product-design/skills/parallel-agents/SKILL.md
  Description: Orchestrate parallel multi-agent development
  Mapped to: (none - this is meta-skill)

product-design:parallel-prompt-generator
  Path: plugins/product-design/skills/parallel-prompt-generator/SKILL.md
  Description: Generate agent-ready prompts from task specs
  Mapped to: (none - used by commands)

python-experts:python-style
  Path: plugins/python-experts/skills/python-style/SKILL.md
  Description: Python coding style, PEP standards, type hints
  Mapped to:
    - python-experts:django-expert
    - python-experts:fastapi-expert
    - python-experts:celery-expert
    - python-experts:python-testing-expert
    - devops-data:data-engineering-expert

...

=== Validation Details ===

Referenced Skills Check:
  ✅ python-experts:python-style exists
  ✅ python-experts:django-dev exists
  ✅ python-experts:django-api exists
  ...

Structure Validation:
  ✅ All skills have valid SKILL.md
  ✅ All frontmatter is valid YAML
  ⚠️  product-design:console-debugging: 'when' field missing

=== Coverage Matrix ===

| Skill | django | fastapi | react | devops | ... |
|-------|--------|---------|-------|--------|-----|
| python-style | ✓ | ✓ | - | - | ... |
| typescript-style | - | - | ✓ | - | ... |
| documentation-research | ✓ | ✓ | - | - | ... |
```

### 6. Fix Mode (--fix)

If `--fix` is specified:

#### 6.1 Remove Invalid References

Delete skills from mapping that don't exist:

```yaml
# Before
python-experts:django-expert:
  skills:
    - python-experts:python-style
    - python-experts:nonexistent-skill  # Will be removed

# After
python-experts:django-expert:
  skills:
    - python-experts:python-style
```

#### 6.2 Suggest Additions (Interactive)

For orphaned skills, prompt user:

```
Found orphaned skill: devops-data:direnv

This skill is about: Environment management (.envrc)

Suggested agents (based on plugin):
  1. devops-data:devops-expert
  2. devops-data:cto-architect
  3. Skip (don't add to any agent)

Add to agent [1/2/3]:
```

#### 6.3 Update Mapping File

After fixes:
```
Fixes Applied:
  - Removed invalid reference: python-experts:nonexistent-skill
  - Added devops-data:direnv to devops-data:devops-expert

Updated: plugins/product-design/skills/parallel-agents/agent-skills-mapping.yaml

Backup saved: agent-skills-mapping.yaml.backup
```

### 7. Exit Codes

- `0`: All validations passed
- `1`: Issues found (invalid references, orphaned skills)
- `2`: Mapping file not found or invalid YAML

---

## Examples

```bash
# Basic review
/review-skills-mapping

# Detailed analysis
/review-skills-mapping --verbose

# Auto-fix issues
/review-skills-mapping --fix

# Fix with detailed output
/review-skills-mapping --fix --verbose
```

## Mapping File Location

The agent-skills-mapping is located at:
```
plugins/product-design/skills/parallel-agents/agent-skills-mapping.yaml
```

## Skill Naming Convention

Skills must use the format `plugin:skill-name`:

| Format | Example | Valid |
|--------|---------|-------|
| `plugin:skill-name` | `python-experts:python-style` | ✅ |
| `skill-name` only | `python-style` | ❌ |
| Wrong plugin | `frontend:python-style` | ❌ |

## Related Commands

| Command | Purpose |
|---------|---------|
| `/forge-refresh` | Refresh plugin cache |
| `/product-design:forge-help` | List all available skills |

## Related Files

| File | Purpose |
|------|---------|
| `agent-skills-mapping.yaml` | Agent-to-skills mapping |
| `plugins/*/skills/*/SKILL.md` | Individual skill definitions |
