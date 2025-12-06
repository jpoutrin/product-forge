---
description: Assess Django codebase readiness for parallel multi-agent development
argument-hint: "[apps-directory]"
---

# parallel-ready-django

**Category**: Parallel Development (Django)

## Usage

```bash
/parallel-ready-django [apps-directory]
```

## Arguments

- `apps-directory`: Optional - Path to Django apps directory (default: `apps/`)

## Purpose

Evaluate a Django codebase for parallelization readiness across 6 dimensions, generating a score from 0-100. This assessment identifies blockers that would cause conflicts during parallel agent execution.

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

### 1. Check Prerequisites

Verify this is a Django project:
```bash
ls manage.py settings.py 2>/dev/null || ls */settings.py 2>/dev/null
```

### 2. Run Analysis Script

Execute the analysis script from the skill references:
```bash
python /path/to/skills/parallel-ready-django/references/analyze-readiness.py [apps-directory]
```

Or perform manual analysis if script unavailable.

### 3. Assess 6 Dimensions

#### Dimension 1: App Boundaries (20 points)

**Check**:
- Count cross-app imports: `grep -r "from apps\." --include="*.py" apps/`
- Identify god apps with >15 models per app
- Check for circular imports between apps

**Scoring**:
- ✅ 20 pts: <10% cross-app imports, no god apps
- ⚠️ 12 pts: 10-30% cross-app imports
- ❌ 5 pts: >30% cross-app imports or god apps

#### Dimension 2: Shared State (20 points)

**Check**:
- Find Django signals: `grep -r "@receiver\|\.connect(" --include="*.py"`
- Find global mutable state: `grep -r "^[a-z_]*\s*=\s*\[\|^[a-z_]*\s*=\s*\{" --include="*.py"`
- Check for singletons and thread-local storage

**Scoring**:
- ✅ 20 pts: No signals, no global mutable state
- ⚠️ 12 pts: <10 signals, limited globals
- ❌ 5 pts: Heavy signal usage or global state

#### Dimension 3: API Contracts (20 points)

**Check**:
- Find serializers with `__all__`: `grep -r 'fields.*__all__' --include="*.py"`
- Check for mypy config: `grep "\[tool.mypy\]" pyproject.toml`
- Check for OpenAPI: `grep -r "spectacular\|swagger" --include="*.py"`

**Scoring**:
- ✅ 20 pts: mypy strict, no `__all__`, OpenAPI present
- ⚠️ 12 pts: Partial typing, some `__all__`
- ❌ 5 pts: No typing, heavy `__all__` usage

#### Dimension 4: Test Infrastructure (15 points)

**Check**:
- Count test files: `find . -name "test_*.py" | wc -l`
- Check pytest config: `grep "pytest" pyproject.toml`
- Check for Factory Boy: `grep -r "DjangoModelFactory" --include="*.py"`

**Scoring**:
- ✅ 15 pts: >20 test files, pytest configured, factories present
- ⚠️ 8 pts: 5-20 test files, partial setup
- ❌ 3 pts: <5 test files, no test framework

#### Dimension 5: Documentation (15 points)

**Check**:
- CLAUDE.md exists
- README.md exists
- Linting configured: `grep "\[tool.ruff\]" pyproject.toml`

**Scoring**:
- ✅ 15 pts: CLAUDE.md + README + ruff
- ⚠️ 8 pts: README + some linting
- ❌ 3 pts: No documentation

#### Dimension 6: Dependencies (10 points)

**Check**:
- Lock file: `ls poetry.lock Pipfile.lock requirements.txt 2>/dev/null`
- Migration count: `find . -path "*/migrations/*.py" -not -name "__init__.py" | wc -l`
- Pinned dependencies in requirements

**Scoring**:
- ✅ 10 pts: Lock file, <50 migrations per app, pinned deps
- ⚠️ 5 pts: Some issues with migrations or deps
- ❌ 2 pts: No lock file, many migrations

### 4. Generate Report

Create/update `.claude/readiness-report.md`:

```markdown
# Django Parallelization Readiness Report

## Overall Score: XX/100

## Dimension Scores

| Dimension | Score | Status |
|-----------|-------|--------|
| App Boundaries | X/20 | ✅/⚠️/❌ |
| Shared State | X/20 | ✅/⚠️/❌ |
| API Contracts | X/20 | ✅/⚠️/❌ |
| Test Infrastructure | X/15 | ✅/⚠️/❌ |
| Documentation | X/15 | ✅/⚠️/❌ |
| Dependencies | X/10 | ✅/⚠️/❌ |

## Blockers (Must Fix Before Parallelization)

[List issues with score <50% in dimension]

## Risks (Should Fix)

[List issues with score 50-80% in dimension]

## What's Working Well

[List items that scored well]

## Recommendations

[Based on score:]
- **Score ≥80**: Ready for parallelization
- **Score 50-79**: Fix blockers, then proceed
- **Score <50**: Sequential work recommended

## Parallelization Potential

- **Recommended parallel tracks**: [1-5 based on app structure]
- **Suggested boundaries**: [Django apps that can work independently]
- **Risk level**: [Low/Medium/High]
```

### 5. Display Summary

Output to console:
```
🔍 Django Parallelization Readiness Assessment

Overall Score: XX/100

┌─────────────────┬───────┬────────┐
│ Dimension       │ Score │ Status │
├─────────────────┼───────┼────────┤
│ App Boundaries  │ XX/20 │ ✅     │
│ Shared State    │ XX/20 │ ⚠️     │
│ API Contracts   │ XX/20 │ ❌     │
│ Tests           │ XX/15 │ ✅     │
│ Documentation   │ XX/15 │ ⚠️     │
│ Dependencies    │ XX/10 │ ✅     │
└─────────────────┴───────┴────────┘

📄 Full report: .claude/readiness-report.md

Next steps:
[if score < 80] → Run /parallel-fix-django to address blockers
[if score ≥ 80] → Run /parallel-decompose <prd-file>
```

## Scoring Thresholds

| Score | Status | Recommendation |
|-------|--------|----------------|
| ≥80 | Ready | Proceed with parallelization |
| 50-79 | Needs Work | Fix high-priority blockers first |
| <50 | Not Ready | Sequential development recommended |

## Example

```bash
# Assess default apps/ directory
/parallel-ready-django

# Assess specific directory
/parallel-ready-django src/apps

# After running
cat .claude/readiness-report.md
```

## Related Commands

- `/parallel-setup` - Initialize infrastructure (run first)
- `/parallel-fix-django` - Fix identified blockers
- `/parallel-decompose` - Create parallel tasks (after score ≥80)
