# Skill Naming Conventions

**Purpose**: Prevent naming collisions across Product Forge plugins
**Last Updated**: 2026-02-04
**Current Status**: ✅ No collisions (115 unique skill names)

## Current State

As of the commands-to-skills migration completion:
- **Total Skills**: 115
- **Unique Names**: 115 (100%)
- **Naming Collisions**: 0
- **Plugins**: 10

## Naming Strategy

### 1. Domain-Specific Prefixes

Use plugin-specific prefixes to ensure uniqueness:

| Plugin | Prefix Pattern | Examples |
|--------|---------------|----------|
| git-workflow | `git-`, `bl-` | `bl-init`, `bl-submit`, `commit`, `rebase` |
| product-design | `prd-`, `qa-`, `parallel-` | `create-prd`, `qa-test`, `parallel-setup` |
| devops-data | `rfc-`, `tech-spec-` | `create-rfc`, `rfc-status`, `tech-spec-status` |
| claude-code-dev | Tool/system specific | `tmux-init`, `install-lsp`, `copy-agent` |
| python-experts | `mypy-`, `django-`, `python-` | `mypy-setup`, `python-mypy`, `django-dev` |
| typescript-experts | `mcp-`, Language specific | `add-mcp-tool`, `create-mcp-server` |
| security-compliance | Domain specific | `oauth`, `mcp-security`, `privacy-compliance` |

### 2. Naming Rules

**Required:**
1. ✅ Use kebab-case (lowercase with hyphens)
2. ✅ Be descriptive and action-oriented
3. ✅ Avoid generic names (`utils`, `helper`, `common`)
4. ✅ Check for existing names before creating new skills

**Recommended:**
1. 📝 Include domain prefix when possible (`prd-`, `qa-`, `bl-`)
2. 📝 Use verb-noun pattern for action skills (`create-prd`, `list-rfcs`)
3. 📝 Keep names under 30 characters
4. 📝 Make names memorable and intuitive

**Forbidden:**
1. ❌ Single-word generic names (unless highly specific, like `rebase`)
2. ❌ Abbreviations without context (`cr`, `pr`, `ts`)
3. ❌ Plugin name as skill name (`product-design`, `git-workflow`)

### 3. Collision Prevention Workflow

Before creating a new skill:

```bash
# Check if skill name already exists
find plugins -path "*/skills/*/SKILL.md" -exec grep "^name: your-skill-name$" {} \;

# List all current skill names
find plugins -path "*/skills/*/SKILL.md" -exec grep "^name:" {} \; | sed 's/name: *//' | sort

# Check for similar names
find plugins -path "*/skills/*/SKILL.md" -exec grep "^name:" {} \; | sed 's/name: *//' | grep "keyword"
```

### 4. High-Risk Name Patterns

These patterns are likely to collide - use with caution:

**High Risk** (avoid unless plugin-prefixed):
- `create`, `list`, `update`, `delete` (generic CRUD)
- `setup`, `init`, `config` (generic operations)
- `test`, `check`, `validate` (generic verification)
- `install`, `deploy`, `build` (generic tooling)

**Better Alternatives**:
- `create` → `create-prd`, `create-rfc`, `create-qa-test`
- `list` → `list-prds`, `list-rfcs`, `list-qa-tests`
- `setup` → `mypy-setup`, `parallel-setup`, `mcp-setup`
- `init` → `bl-init`, `tmux-init`

### 5. Name Collision Resolution

If a collision occurs:

**Option A: Add Plugin Prefix**
- Before: `create` (ambiguous)
- After: `product-design:create` (explicit)

**Option B: Add Domain Prefix**
- Before: `create` (ambiguous)
- After: `create-prd`, `create-rfc` (specific)

**Option C: Rename Existing Skill**
- Before: Generic name in old skill
- After: More specific name + maintain backward compatibility

### 6. Reserved Names

The following names are reserved for core functionality:

- `help`, `version`, `config`, `settings`
- `agent`, `skill`, `command`, `plugin`
- `install`, `uninstall`, `update`, `refresh`

### 7. Plugin-Specific Namespaces

Each plugin has implicit namespace conventions:

**git-workflow**: Git operations and branchless workflow
- `bl-*` - Branchless operations
- `git-*` - Standard git operations
- Git verbs: `commit`, `rebase`, `merge`

**product-design**: Product development and documentation
- `prd-*` - Product Requirements Documents
- `qa-*` - Quality Assurance
- `parallel-*` - Parallel development
- `create-persona`, `brainstorm-solution`

**devops-data**: Infrastructure and data engineering
- `rfc-*` - Request for Comments
- `tech-spec-*` - Technical Specifications
- Cloud providers: `aws-*`, `gcp-*`
- Data tools: `dbt`, `sqlmesh`, `ansible`

**claude-code-dev**: Developer tooling and workflows
- `copy-*` - Copying utilities
- `install-*` - Installation scripts
- `propose-*` - Feedback and improvement
- `tmux-*`, `mcp-*`

**python-experts**: Python tooling and frameworks
- `mypy-*` - Type checking
- `django-*` - Django framework
- `python-*` - Python-specific

**typescript-experts**: TypeScript and MCP development
- `mcp-*` - MCP server development
- `add-mcp-*` - MCP components
- TypeScript tooling

### 8. Collision Detection Script

Use this script to check for collisions:

```bash
#!/bin/bash
# check-skill-collisions.sh

echo "Checking for skill name collisions..."
COLLISIONS=$(find plugins -path "*/skills/*/SKILL.md" -exec grep "^name:" {} \; | \
  sed 's/name: *//' | sort | uniq -d)

if [ -z "$COLLISIONS" ]; then
  echo "✓ No collisions found"
  exit 0
else
  echo "⚠ WARNING: Collisions detected:"
  echo "$COLLISIONS"
  exit 1
fi
```

### 9. Best Practices Examples

**Good Skill Names:**
```yaml
# Clear domain prefix
name: prd-status
name: qa-test-management
name: bl-submit

# Descriptive action-object
name: create-tech-spec
name: generate-tasks
name: install-playwright-mcp

# Domain-specific term
name: branchless-workflow
name: conventional-commits
```

**Avoid:**
```yaml
# Too generic
name: create
name: list
name: helper

# Ambiguous abbreviation
name: prd
name: qa
name: ts

# Not descriptive
name: tool
name: utility
name: utils
```

### 10. Migration Notes

**From Commands to Skills:**
- All 56 migrated commands retained their original names
- No collisions introduced during migration
- All names follow existing conventions

**Future Migrations:**
- Always check for collisions before migrating
- Prefer adding domain prefixes over renaming
- Document any renaming decisions

## Monitoring

**Regular Checks:**
1. Run collision detection before each release
2. Review new skill names in PR reviews
3. Update this document when adding new naming patterns

**Current Stats** (as of 2026-02-04):
- Skills: 115
- Collisions: 0
- Plugins: 10
- Avg skills per plugin: 11.5

## Conclusion

The current naming strategy has successfully prevented collisions across 115 skills. Following these conventions will maintain this zero-collision state as the project grows.

**Key Takeaway**: Use domain-specific prefixes and avoid generic names to prevent collisions.
