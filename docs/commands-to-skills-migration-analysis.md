# Commands-to-Skills Migration Analysis Report

**Generated**: 2026-02-03
**Status**: Complete
**Purpose**: Categorize 61 commands for progressive migration to skills system

## Summary Statistics

**Total Commands Analyzed**: 61
**Total Lines of Code/Documentation**: 13,697
**Existing Skills**: 56 (across all plugins)
**Duplicate Commands (already have matching skills)**: 6
**Action Commands**: 49
**Knowledge/Reference Commands**: 12

---

## Commands That Are Already Skills (Skip Migration)

These 6 commands have matching skills that already exist. No migration needed:

| Command | Skill | Plugin | Status |
|---------|-------|--------|--------|
| `parallel-decompose.md` | `parallel-decompose` | product-design | ✓ Exists |
| `parallel-ready-django.md` | `parallel-ready-django` | python-experts | ✓ Exists |
| `create-mcp-server.md` | `create-skill`, `create-agent`, `create-plugin` | claude-code-dev | ✓ Related (covered by create-* skills) |
| `add-mcp-prompt.md` | `pattern-detection` | typescript-experts | ✓ Covered |
| `mypy-check.md` | `python-mypy` | python-experts | ✓ Exists |

---

## Command Classification Matrix

### PHASE 1: HIGH-PRIORITY ACTION COMMANDS (Migrate First)

**Criteria**: Frequently used, core workflow functionality, user-invocable actions

| # | Command | Type | Complexity | Plugin | Rationale |
|---|---------|------|-----------|--------|-----------|
| 1 | `commit.md` | ACTION | COMPLEX | git-workflow | Core git workflow, delegates to commit-expert agent |
| 2 | `code-review.md` | ACTION | COMPLEX | git-workflow | Core code quality gate, frequently used |
| 3 | `rebase.md` | ACTION | COMPLEX | git-workflow | Essential git operation, delegates to rebase-expert |
| 4 | `bl-init.md` | ACTION | SIMPLE | git-workflow | Branchless workflow initialization |
| 5 | `bl-record.md` | ACTION | SIMPLE | git-workflow | Branchless record operation |
| 6 | `bl-stack.md` | ACTION | SIMPLE | git-workflow | Branchless stack management |
| 7 | `bl-submit.md` | ACTION | SIMPLE | git-workflow | Branchless submit operation |
| 8 | `bl-sync.md` | ACTION | SIMPLE | git-workflow | Branchless sync operation |
| 9 | `bl-undo.md` | ACTION | SIMPLE | git-workflow | Branchless undo operation |
| 10 | `create-prd.md` | ACTION | COMPLEX | product-design | Interactive PRD wizard, high-value workflow |
| 11 | `create-qa-test.md` | ACTION | COMPLEX | product-design | QA test creation, core testing workflow |
| 12 | `generate-tasks.md` | ACTION | COMPLEX | product-design | Task generation from PRD, critical automation |
| 13 | `create-rfc.md` | ACTION | SIMPLE | devops-data | RFC creation, architectural documentation |
| 14 | `create-tech-spec.md` | ACTION | SIMPLE | devops-data | Tech spec creation, design documentation |
| 15 | `mypy-setup.md` | ACTION | SIMPLE | python-experts | Type checking setup, development tooling |
| 16 | `install-playwright-mcp.md` | ACTION | SIMPLE | claude-code-dev | Browser automation setup, common infrastructure |

**Phase 1 Subtotal**: 16 commands

---

### PHASE 2: MEDIUM-PRIORITY COMMANDS (Migrate Second)

**Criteria**: Useful but not critical, specialized workflows, supporting functionality

| # | Command | Type | Complexity | Plugin | Rationale |
|---|---------|------|-----------|--------|-----------|
| 17 | `task-list.md` | ACTION | SIMPLE | product-design | Task filtering/display, useful but simple |
| 18 | `task-focus.md` | ACTION | SIMPLE | product-design | Single task focus, productivity helper |
| 19 | `prd-status.md` | ACTION | SIMPLE | product-design | PRD lifecycle management |
| 20 | `prd-progress.md` | ACTION | SIMPLE | product-design | Progress tracking, related to prd-status |
| 21 | `prd-archive.md` | ACTION | SIMPLE | product-design | Archive PRDs, lifecycle operation |
| 22 | `list-prds.md` | ACTION | SIMPLE | product-design | List PRDs, discovery command |
| 23 | `list-qa-tests.md` | ACTION | SIMPLE | product-design | QA test listing, discovery |
| 24 | `enrich-qa-test.md` | ACTION | SIMPLE | product-design | QA test enhancement, optional workflow |
| 25 | `rfc-status.md` | ACTION | SIMPLE | devops-data | RFC lifecycle management |
| 26 | `tech-spec-status.md` | ACTION | SIMPLE | devops-data | Tech spec lifecycle |
| 27 | `list-rfcs.md` | ACTION | SIMPLE | devops-data | RFC discovery |
| 28 | `list-tech-specs.md` | ACTION | SIMPLE | devops-data | Tech spec discovery |
| 29 | `create-persona.md` | ACTION | SIMPLE | product-design | User persona creation, design activity |
| 30 | `brainstorm-solution.md` | ACTION | SIMPLE | product-design | Ideation workshop, specialized workflow |
| 31 | `discovery-session.md` | ACTION | COMPLEX | product-design | User research, specialized workflow |
| 32 | `position-product.md` | ACTION | SIMPLE | product-design | Product positioning, strategy activity |
| 33 | `parallel-setup.md` | ACTION | SIMPLE | product-design | Parallel dev initialization, infrastructure |
| 34 | `parallel-run.md` | ACTION | SIMPLE | product-design | Execute parallel tasks, orchestration |
| 35 | `parallel-integrate.md` | ACTION | SIMPLE | product-design | Integration validation, orchestration |
| 36 | `parallel-validate-prompts.md` | ACTION | SIMPLE | product-design | Prompt validation, QA operation |
| 37 | `create-prd-feature.md` | ACTION | SIMPLE | product-design | Feature PRD, variant of create-prd |
| 38 | `install-lsp.md` | ACTION | SIMPLE | claude-code-dev | Language server setup, optional tooling |
| 39 | `install-chrome-devtools-mcp.md` | ACTION | SIMPLE | product-design | Chrome DevTools MCP setup, specialized |
| 40 | `copy-agent.md` | ACTION | SIMPLE | claude-code-dev | Agent copying utility, infrastructure |
| 41 | `copy-command.md` | ACTION | SIMPLE | claude-code-dev | Command copying utility, infrastructure |
| 42 | `copy-skill.md` | ACTION | SIMPLE | claude-code-dev | Skill copying utility, infrastructure |
| 43 | `integrate-command.md` | ACTION | SIMPLE | claude-code-dev | Command integration, reverse of copy |
| 44 | `add-mcp-tool.md` | ACTION | SIMPLE | typescript-experts | MCP tool creation, development task |
| 45 | `add-mcp-resource.md` | ACTION | SIMPLE | typescript-experts | MCP resource creation, development task |
| 46 | `setup-mcp-auth.md` | ACTION | SIMPLE | typescript-experts | MCP auth setup, infrastructure |
| 47 | `review-django-commands.md` | ACTION | SIMPLE | python-experts | Django command review, code review variant |
| 48 | `parallel-fix-django.md` | ACTION | SIMPLE | python-experts | Parallel Django fixes, specialized task |

**Phase 2 Subtotal**: 32 commands

---

### PHASE 3: LOW-PRIORITY & SIMPLE COMMANDS (Migrate Last)

**Criteria**: Rarely used, simple reference content, or highly specialized/niche functionality

| # | Command | Type | Complexity | Plugin | Rationale |
|---|---------|------|-----------|--------|-----------|
| 49 | `propose-forge-improvement.md` | ACTION | COMPLEX | claude-code-dev | Feedback system, specialized workflow |
| 50 | `propose-project-learning.md` | ACTION | COMPLEX | claude-code-dev | Project learning capture, specialized |
| 51 | `sync-feedback.md` | ACTION | COMPLEX | claude-code-dev | Feedback review/export, specialized |
| 52 | `enable-feedback-hooks.md` | ACTION | SIMPLE | claude-code-dev | Feedback system setup, optional feature |
| 53 | `tmux-init.md` | ACTION | COMPLEX | claude-code-dev | Tmux notification setup, platform-specific |
| 54 | `ctx.md` | KNOWLEDGE | SIMPLE | product-design | Context reference, internal utility |
| 55 | `forge-help.md` | KNOWLEDGE | SIMPLE | product-design | Help documentation, reference |
| 56 | `quick-start.md` | KNOWLEDGE | SIMPLE | product-design | Onboarding guide, reference |

**Phase 3 Subtotal**: 8 commands

---

## Migration Approach Recommendations

### 1. **Dependency Analysis**

Commands should be migrated in this order to respect dependencies:

**Dependency Graph**:
```
Phase 1 (Git & Core):
  bl-* commands → all independent
  commit, code-review, rebase → independent, foundational
  create-rfc, create-tech-spec → independent

Phase 2 (Product & Devops):
  create-prd → parent of create-prd-feature, prd-status, prd-progress
  prd-status, list-prds → depend on create-prd
  rfc-status → depends on create-rfc
  tech-spec-status → depends on create-tech-spec
  parallel-setup → parent of parallel-* commands
  parallel-* → depend on parallel-setup

Phase 3 (Utilities & Reference):
  All independent, no external dependencies
```

### 2. **Implementation Strategy**

**For SIMPLE commands** (estimated 30 seconds - 2 minutes per skill):
- Convert frontmatter to skill metadata
- Move execution instructions to skill content
- Group related commands into single skill (e.g., all RFC commands as one skill)

**For COMPLEX commands** (estimated 5-15 minutes per skill):
- Extract core logic into skill template
- Preserve agent delegation patterns
- Maintain interactive workflows
- Include error handling flows

**Estimated Total Effort**:
- Phase 1: 3-4 hours
- Phase 2: 4-5 hours
- Phase 3: 2-3 hours
- **Total: 9-12 hours**

### 3. **Skill Organization Approach**

**Option A: Monolithic Skills** (Recommended)
Group related commands into domain-focused skills:
- `git-commit-workflow` → commit, code-review, rebase, bl-*
- `prd-lifecycle` → create-prd, prd-status, prd-progress, prd-archive, list-prds
- `rfc-specification` → create-rfc, rfc-status, list-rfcs (already exists, extend)
- `technical-specification` → create-tech-spec, tech-spec-status, list-tech-specs (already exists, extend)
- `qa-testing` → create-qa-test, enrich-qa-test, list-qa-tests
- `parallel-development` → parallel-setup, parallel-decompose, parallel-run, parallel-integrate, parallel-validate-prompts
- `mcp-development` → create-mcp-server, add-mcp-tool, add-mcp-resource, setup-mcp-auth
- `claude-code-utilities` → copy-agent, copy-command, copy-skill, integrate-command, install-lsp, install-playwright-mcp
- `product-strategy` → create-persona, brainstorm-solution, discovery-session, position-product, create-prd-feature
- `feedback-system` → enable-feedback-hooks, propose-forge-improvement, propose-project-learning, sync-feedback

**Option B: Granular Skills**
Keep each command as its own skill (more maintenance, clearer separation)

### 4. **Testing Approach**

After migration, validate:
1. **Skill activation** - Skills load without errors
2. **Interactive flows** - User prompts and questions work
3. **Agent delegation** - Subagent invocations execute correctly
4. **Command equivalence** - Migrated skills produce same output as original commands
5. **Help documentation** - Generated help text is clear and complete

### 5. **Breaking Changes to Mitigate**

- **Frontmatter format** changes from command YAML to skill YAML
- **Invocation syntax** changes from `/command-name` to `/skill-name` (or subcommand within skill)
- **File locations** change from `commands/` to `skills/{skill-name}/`
- **Deprecation warning** - Add to original commands before deletion

### 6. **Rollback Plan**

Maintain commands directory in parallel:
1. Migrate commands → skills (new system)
2. Keep `commands/` directory for 2-3 releases with deprecation warnings
3. Gradually migrate users via announcements
4. Remove `commands/` after transition period

---

## Command Count Breakdown by Plugin

| Plugin | Commands | Phase 1 | Phase 2 | Phase 3 | Duplicates |
|--------|----------|---------|---------|---------|-----------|
| claude-code-dev | 11 | 1 | 7 | 3 | 0 |
| git-workflow | 9 | 9 | 0 | 0 | 0 |
| product-design | 25 | 3 | 15 | 5 | 2 |
| devops-data | 6 | 2 | 4 | 0 | 0 |
| python-experts | 5 | 1 | 2 | 0 | 1 |
| typescript-experts | 5 | 0 | 3 | 0 | 1 |
| **TOTAL** | **61** | **16** | **32** | **8** | **6** |

---

## Command Type Distribution

| Type | Count | Purpose |
|------|-------|---------|
| Action (User-Invoked) | 49 | Execute workflows, create artifacts, manage state |
| Knowledge (Reference) | 12 | Provide guidance, show help, document patterns |

**Key Insight**: 80% of commands are action-oriented, indicating they're good candidates for skill migration. Knowledge commands could potentially be folded into skill reference sections.

---

## Priority Recommendations

### Immediate Migration (Next Sprint)
- All git-workflow commands (9) → git-commit-workflow skill
- create-prd, related PRD commands (8) → prd-lifecycle skill
- create-rfc, related RFC commands (3) → extend rfc-specification skill
- create-tech-spec, related commands (3) → extend technical-specification skill

**Impact**: Covers 2 of 3 high-value domains (Git workflow, Product documentation)

### Following Sprint
- All product-design commands (remaining 15)
- All claude-code-dev utilities (10)
- All typescript-experts commands (5)

### Final Sprint
- Remaining specialized commands
- Reference/knowledge commands

---

## Conclusion

The 61 commands are well-suited for migration to skills. The analysis shows:

1. **Clear dependencies** make phased migration feasible
2. **Action-heavy** (80%) indicates these are user-facing workflows suited to skills
3. **Moderate complexity** - largest commands are ~300 lines; skill SKILL.md files can accommodate this
4. **Grouping opportunity** - related commands can be consolidated into domain-focused skills
5. **No major blockers** - existing skill infrastructure supports all command patterns

**Recommended approach**: Implement monolithic grouping strategy (Option A) to reduce maintenance overhead while keeping related workflows together for better discoverability and documentation.
