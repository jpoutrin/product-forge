# Skill Best Practices

**Purpose**: Guidelines for creating, maintaining, and organizing Claude Code skills in Product Forge
**Last Updated**: 2026-02-04
**Status**: Official guidelines based on 56-skill migration project

## Table of Contents

1. [Skills vs Commands](#skills-vs-commands)
2. [Frontmatter Best Practices](#frontmatter-best-practices)
3. [User-Invocable vs Knowledge Skills](#user-invocable-vs-knowledge-skills)
4. [Naming Conventions](#naming-conventions)
5. [Directory Structure](#directory-structure)
6. [Content Organization](#content-organization)
7. [Supporting Files](#supporting-files)
8. [Testing Skills](#testing-skills)
9. [Common Pitfalls](#common-pitfalls)
10. [Migration Patterns](#migration-patterns)

---

## Skills vs Commands

### Why Skills Are Preferred

**Skills offer:**
- ✅ Supporting files and subdirectories
- ✅ Better invocation control (`user-invocable` flag)
- ✅ Context forking capability (`context: fork`)
- ✅ Auto-loading for knowledge skills
- ✅ More flexible metadata
- ✅ Official Claude Code recommendation

**Commands are:**
- ⚠️ Deprecated (backward compatible but not recommended)
- ⚠️ Limited to single .md file
- ⚠️ Less flexible metadata
- ⚠️ No supporting files

### When to Create a Skill

Create a skill when:
1. ✅ Users need to invoke an action (e.g., `/create-prd`)
2. ✅ Claude needs reference material that auto-loads (knowledge skills)
3. ✅ You need supporting files (templates, examples, schemas)
4. ✅ The functionality is complex enough to warrant its own namespace

Don't create a skill for:
1. ❌ One-time operations better suited for scripts
2. ❌ Content that belongs in existing skills
3. ❌ Overly generic utilities without clear use cases

---

## Frontmatter Best Practices

### Required Fields

```yaml
---
name: skill-name
description: Clear, concise description of what the skill does and when to use it
---
```

### Optional Fields

```yaml
---
name: skill-name
description: Clear description
user-invocable: false          # For knowledge/auto-loading skills
argument-hint: "[options]"     # Usage hint for action skills
allowed-tools: Read, Write     # Tool restrictions
model: haiku                   # Override default model
context: fork                  # Run in isolated context
hooks:
  - pre-invoke                 # Lifecycle hooks
---
```

### Field Guidelines

**name**:
- Use kebab-case
- Be specific (avoid generic names)
- Follow naming conventions (see below)
- Must match directory name

**description**:
- Start with action verb for action skills ("Create...", "List...", "Deploy...")
- Describe trigger conditions for knowledge skills ("Use when...", "Auto-loads when...")
- Be specific about use cases
- Keep under 200 characters

**user-invocable**:
- Default: `true` (users can invoke with `/skill-name`)
- Set to `false` for knowledge/reference skills that auto-load
- Omit field if `true` (default behavior)

**argument-hint**:
- Show expected arguments
- Use square brackets for optional: `[--option]`
- Use angle brackets for required: `<name>`
- Example: `<prd-file> [--output-dir <dir>]`

### Frontmatter Examples

**Action Skill (User-Invocable)**:
```yaml
---
name: create-prd
description: Interactive PRD creation wizard with comprehensive question flow
argument-hint: "<product-name>"
---
```

**Knowledge Skill (Auto-Loading)**:
```yaml
---
name: git-commits
description: Git commit best practices with conventional commits format and atomic commit principles. Use when committing code to ensure clear, meaningful commit history with proper type prefixes and semantic versioning support.
user-invocable: false
---
```

**Complex Action Skill**:
```yaml
---
name: parallel-decompose
description: Decompose PRDs and Tech Specs into parallel-executable tasks with contracts, prompts, and dependency tracking. Use when setting up multi-agent parallel development.
argument-hint: "<spec-file> [--output-dir <dir>] [--max-agents <n>]"
context: fork
allowed-tools: Read, Write, Glob, Grep
---
```

---

## User-Invocable vs Knowledge Skills

### User-Invocable Skills (Default)

**Purpose**: Users explicitly invoke to trigger actions

**Characteristics**:
- Users invoke with `/skill-name`
- Execute specific workflows
- Often interactive
- Return results or create artifacts

**Examples**:
- `/create-prd` - Create a new PRD
- `/bl-init` - Initialize git-branchless
- `/generate-tasks` - Convert PRD to tasks

**Frontmatter**:
```yaml
---
name: create-prd
description: Interactive PRD creation wizard
# user-invocable: true (default, can omit)
---
```

### Knowledge Skills (Auto-Loading)

**Purpose**: Provide context and conventions automatically

**Characteristics**:
- Auto-load when context matches
- Provide reference material
- Enforce conventions
- Guide Claude's behavior

**Examples**:
- `git-commits` - Commit message conventions
- `python-style` - Python coding standards
- `prd-management` - PRD organization rules

**Frontmatter**:
```yaml
---
name: git-commits
description: Git commit best practices with conventional commits format. Use when committing code to ensure clear, meaningful commit history.
user-invocable: false
---
```

### Choosing Between Types

**Make it user-invocable if**:
- Users need to explicitly trigger it
- It performs specific actions
- It creates or modifies artifacts
- It has interactive workflows

**Make it knowledge skill if**:
- It provides conventions or patterns
- It should auto-load based on context
- It guides Claude's behavior
- It's reference documentation

---

## Naming Conventions

**See**: `docs/skill-naming-conventions.md` for complete guidelines

### Quick Reference

**Good Names**:
- `create-prd` - Action + object
- `prd-status` - Domain prefix + action
- `bl-init` - Namespace + action
- `python-mypy` - Language + tool

**Avoid**:
- `create` - Too generic
- `prd` - Not descriptive
- `helper` - Vague
- `utils` - Non-specific

### Collision Prevention

```bash
# Check for existing names before creating
find plugins -path "*/skills/*/SKILL.md" -exec grep "^name: my-skill-name$" {} \;
```

**Current Status**: 115 unique skill names, 0 collisions

---

## Directory Structure

### Basic Skill Structure

```
skills/
└── skill-name/
    └── SKILL.md              # Required: Main skill definition
```

### Skill with Supporting Files

```
skills/
└── skill-name/
    ├── SKILL.md              # Required: Main skill definition
    ├── examples/             # Optional: Example files
    │   ├── basic-example.md
    │   └── advanced-example.md
    ├── templates/            # Optional: Template files
    │   ├── template.yaml
    │   └── template.md
    └── schemas/              # Optional: Schema definitions
        └── schema.json
```

### Directory Naming Rules

1. ✅ Use kebab-case
2. ✅ Match the skill name exactly
3. ✅ Keep names concise but descriptive
4. ✅ Group related skills by plugin

### Example Plugin Structure

```
plugins/product-design/
├── agents/
│   └── prd-orchestrator.md
├── skills/
│   ├── create-prd/
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── prd-template.md
│   ├── prd-status/
│   │   └── SKILL.md
│   ├── prd-management/         # Knowledge skill
│   │   └── SKILL.md
│   └── qa-testing-methodology/ # Knowledge skill
│       └── SKILL.md
└── manifest.json
```

---

## Content Organization

### SKILL.md Structure

```markdown
---
name: skill-name
description: Brief description
argument-hint: "<args> [options]"
---

# Skill Title

Brief overview of what the skill does.

## Usage

\`\`\`bash
/skill-name <args> [options]
\`\`\`

## Arguments

- `<arg>`: Required - Description
- `[option]`: Optional - Description

## Examples

### Example 1: Basic Usage
\`\`\`bash
/skill-name basic-arg
\`\`\`

### Example 2: Advanced Usage
\`\`\`bash
/skill-name arg --option value
\`\`\`

## Execution Instructions

1. **Step 1**: What to do first
2. **Step 2**: What to do next
3. **Step 3**: How to verify

## Interactive Flow (if applicable)

\`\`\`
User: /skill-name

Agent: Starting workflow...
[Interactive prompts and responses]
\`\`\`

## Error Handling

| Error | Resolution |
|-------|------------|
| Error 1 | How to fix |
| Error 2 | How to fix |

## See Also

- Related skill links
- Documentation links
```

### Content Guidelines

**Do**:
- ✅ Start with clear overview
- ✅ Provide concrete examples
- ✅ Include error handling
- ✅ Document interactive flows
- ✅ Add troubleshooting section
- ✅ Link to related skills

**Don't**:
- ❌ Include placeholder text
- ❌ Leave sections incomplete
- ❌ Use vague descriptions
- ❌ Forget to update examples
- ❌ Mix multiple concerns

---

## Supporting Files

### When to Add Supporting Files

Add supporting files when:
1. ✅ Skills need templates (PRD templates, config templates)
2. ✅ Examples are too long for main SKILL.md
3. ✅ Schemas or specifications are needed
4. ✅ Multiple variations exist

### Supporting File Types

**templates/**:
- Reusable templates
- Configuration files
- Scaffolding structures

**examples/**:
- Complete working examples
- Use case demonstrations
- Before/after comparisons

**schemas/**:
- JSON schemas
- YAML specifications
- Data structure definitions

**docs/**:
- Extended documentation
- Architecture diagrams
- Decision records

### Referencing Supporting Files

In SKILL.md:
```markdown
## Template

See `templates/prd-template.md` for the full PRD template structure.

## Examples

Complete examples are available in:
- `examples/basic-prd.md` - Simple product example
- `examples/feature-prd.md` - Feature-specific example
```

---

## Testing Skills

### Pre-Deployment Testing

**1. Frontmatter Validation**:
```bash
# Check required fields
grep "^name:" plugins/*/skills/*/SKILL.md
grep "^description:" plugins/*/skills/*/SKILL.md

# Check for proper closing
head -20 plugins/*/skills/*/SKILL.md | grep "^---$"
```

**2. Name Consistency**:
```bash
# Verify name matches directory
for skill in plugins/*/skills/*/SKILL.md; do
  DIR=$(basename $(dirname "$skill"))
  NAME=$(grep "^name:" "$skill" | sed 's/name: *//')
  if [ "$DIR" != "$NAME" ]; then
    echo "Mismatch: $skill"
  fi
done
```

**3. Collision Detection**:
```bash
# Check for duplicate names
find plugins -path "*/skills/*/SKILL.md" -exec grep "^name:" {} \; | \
  sed 's/name: *//' | sort | uniq -d
```

**4. Content Validation**:
```bash
# Check minimum content length
for skill in plugins/*/skills/*/SKILL.md; do
  LINES=$(wc -l < "$skill")
  if [ $LINES -lt 20 ]; then
    echo "Short skill: $skill ($LINES lines)"
  fi
done
```

### Post-Deployment Testing

**1. Load Test**:
```bash
# Refresh plugins to load skills
/forge-refresh --force
```

**2. Invocation Test**:
- Test user-invocable skills: `/skill-name --help`
- Verify knowledge skills auto-load in relevant contexts

**3. Functional Test**:
- Execute sample workflows
- Verify interactive prompts work
- Check error handling

---

## Common Pitfalls

### 1. Name Mismatches

❌ **Wrong**:
```
Directory: create-prd
SKILL.md: name: prd-create
```

✅ **Correct**:
```
Directory: create-prd
SKILL.md: name: create-prd
```

### 2. Missing user-invocable for Knowledge Skills

❌ **Wrong**:
```yaml
---
name: git-commits
description: Git commit conventions
# Missing user-invocable: false
---
```

✅ **Correct**:
```yaml
---
name: git-commits
description: Git commit conventions
user-invocable: false
---
```

### 3. Vague Descriptions

❌ **Wrong**:
```yaml
description: Helps with PRDs
```

✅ **Correct**:
```yaml
description: Interactive PRD creation wizard with comprehensive question flow. Use when starting a new product or feature to document requirements systematically.
```

### 4. Incomplete Frontmatter

❌ **Wrong**:
```yaml
---
name: create-prd
---
```

✅ **Correct**:
```yaml
---
name: create-prd
description: Interactive PRD creation wizard
argument-hint: "<product-name>"
---
```

### 5. Generic Naming

❌ **Wrong**:
```yaml
name: create
name: list
name: helper
```

✅ **Correct**:
```yaml
name: create-prd
name: list-rfcs
name: prd-management
```

### 6. Mixed Concerns

❌ **Wrong**: One skill doing multiple unrelated things
```yaml
name: prd-and-qa-and-tasks
description: Creates PRDs, QA tests, and task lists
```

✅ **Correct**: Separate focused skills
```yaml
name: create-prd
description: Interactive PRD creation wizard

name: create-qa-test
description: Create QA test procedure

name: generate-tasks
description: Convert PRD to task list
```

---

## Migration Patterns

### From Command to Skill

**Command Structure**:
```
commands/
└── command-name.md
```

**Skill Structure**:
```
skills/
└── command-name/
    └── SKILL.md
```

**Migration Steps**:
1. Create skill directory: `mkdir -p plugins/plugin-name/skills/command-name`
2. Create SKILL.md with proper frontmatter
3. Copy command content (everything after frontmatter)
4. Test the skill
5. Remove old command file

**Frontmatter Conversion**:

Command:
```yaml
---
description: Creates a new PRD
argument-hint: "<product-name>"
---
```

Skill:
```yaml
---
name: create-prd
description: Creates a new PRD
argument-hint: "<product-name>"
---
```

### Consolidating Multiple Commands

When multiple related commands exist, consider consolidating:

**Before (Multiple Commands)**:
```
commands/
├── prd-create.md
├── prd-status.md
├── prd-archive.md
└── prd-list.md
```

**Option A: Keep Separate (Recommended)**:
```
skills/
├── create-prd/
├── prd-status/
├── prd-archive/
└── list-prds/
```

**Option B: Consolidate (Only if highly related)**:
```
skills/
└── prd-lifecycle/
    ├── SKILL.md          # Handles all PRD operations
    └── docs/
        └── subcommands.md
```

### Breaking Up Large Skills

If a skill becomes too large (>500 lines), consider splitting:

**Before**:
```
skills/
└── mega-skill/
    └── SKILL.md (800 lines)
```

**After**:
```
skills/
├── core-skill/
│   └── SKILL.md (200 lines)
├── advanced-skill/
│   └── SKILL.md (200 lines)
└── skill-utilities/      # Knowledge skill
    └── SKILL.md (150 lines, user-invocable: false)
```

---

## Quick Checklist

Use this checklist when creating new skills:

### Creation Phase
- [ ] Skill name is unique (checked for collisions)
- [ ] Name follows conventions (kebab-case, descriptive)
- [ ] Directory name matches skill name
- [ ] SKILL.md created with frontmatter

### Frontmatter Phase
- [ ] `name:` field present and correct
- [ ] `description:` field clear and specific
- [ ] `user-invocable:` set correctly (false for knowledge skills)
- [ ] `argument-hint:` included for action skills
- [ ] Frontmatter properly closed with `---`

### Content Phase
- [ ] Clear overview provided
- [ ] Usage examples included
- [ ] Execution instructions documented
- [ ] Error handling covered
- [ ] Interactive flows documented (if applicable)
- [ ] Related skills linked

### Testing Phase
- [ ] Frontmatter validates
- [ ] Name matches directory
- [ ] No collisions with other skills
- [ ] Content is substantial (>20 lines)
- [ ] Skill loads in Claude Code
- [ ] Invocation works as expected

### Deployment Phase
- [ ] Run `/forge-refresh --force`
- [ ] Test skill invocation
- [ ] Verify auto-loading (for knowledge skills)
- [ ] Update documentation

---

## Resources

**Related Documentation**:
- `docs/skill-naming-conventions.md` - Naming guidelines and collision prevention
- `docs/skill-migration-test-results.md` - Testing results and validation
- `docs/commands-to-skills-migration-analysis.md` - Migration project analysis

**Claude Code Documentation**:
- Skills specification (official Claude Code docs)
- Frontmatter reference
- Tool permissions

**Project Stats** (as of 2026-02-04):
- Total Skills: 115
- Newly Migrated: 56
- Plugins: 10
- Zero Collisions: ✅

---

## Conclusion

Following these best practices ensures:
1. ✅ Consistent skill quality across Product Forge
2. ✅ Easy discovery and maintenance
3. ✅ No naming collisions
4. ✅ Clear documentation
5. ✅ Smooth user experience

**Remember**: Skills are the recommended approach for extending Claude Code. Take time to design them well, and they'll serve users for years to come.
