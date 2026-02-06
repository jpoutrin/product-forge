# forge-hooks CLI Expansion Plan

## Current State

The `forge-hooks` CLI currently has:
- **validate** command group with 3 validators:
  - `new-file` - Validate new file creation
  - `contains` - Validate file content requirements
  - `ownership` - Validate file ownership rules

## Proposed Additions

### 1. YouTube Transcript Fetcher

**Current location:** `scripts/fetch-youtube-transcript.py`

**Proposed command:** `forge-hooks youtube <url> [--output DIR]`

**Purpose:** Fetch YouTube video transcripts and save as readable text files

**Usage:**
```bash
forge-hooks youtube "https://www.youtube.com/watch?v=4_2j5wgt_ds"
forge-hooks youtube "https://youtu.be/4_2j5wgt_ds" --output .work/transcripts
```

**Dependencies:** `youtube-transcript-api`

**Implementation:**
- Create `src/forge_hooks/utils/youtube.py` with core logic
- Add CLI command in `src/forge_hooks/cli.py`
- Add dependency to `pyproject.toml` as optional extra: `youtube`

---

### 2. Marketplace Validator

**Current location:** `scripts/validate-marketplace.py`

**Proposed command:** `forge-hooks validate marketplace [PATH]`

**Purpose:** Validate marketplace.json against Claude Code schema

**Usage:**
```bash
forge-hooks validate marketplace
forge-hooks validate marketplace .claude-plugin/marketplace.json
```

**Dependencies:** `jsonschema`, `requests`

**Implementation:**
- Create `src/forge_hooks/validators/marketplace.py`
- Add to existing `validate` command group
- Add dependencies to `pyproject.toml` as optional extra: `marketplace`

---

### 3. Forge Index Generator

**Current location:** `scripts/generate-forge-index.py`

**Proposed command:** `forge-hooks index [--output FILE] [--format md|json]`

**Purpose:** Generate index of all Product Forge agents, skills, and commands

**Usage:**
```bash
forge-hooks index
forge-hooks index --output forge-index.md --format md
forge-hooks index --output forge-index.json --format json
```

**Dependencies:** None (stdlib only)

**Implementation:**
- Create `src/forge_hooks/utils/indexer.py` with core logic
- Add CLI command in `src/forge_hooks/cli.py`
- No extra dependencies needed

---

### 4. Feedback Manager

**Current location:** `scripts/hooks/save-feedback.py`

**Proposed command:** `forge-hooks feedback <subcommand>`

**Purpose:** Manage Product Forge feedback and learnings

**Subcommands:**
```bash
# Save feedback from stdin (used by hooks)
forge-hooks feedback save

# List feedback items
forge-hooks feedback list [--project SLUG] [--type TYPE]

# Show statistics
forge-hooks feedback stats

# Sync feedback to Product Forge
forge-hooks feedback sync [--project SLUG]
```

**Dependencies:** None (stdlib only)

**Implementation:**
- Create `src/forge_hooks/feedback/` module
  - `manager.py` - Core feedback management
  - `stats.py` - Statistics tracking
  - `sync.py` - Sync to Product Forge
- Add CLI command group in `src/forge_hooks/cli.py`

---

## Proposed CLI Structure

```
forge-hooks
├── validate              # Validation commands
│   ├── new-file         # ✅ Existing
│   ├── contains         # ✅ Existing
│   ├── ownership        # ✅ Existing
│   └── marketplace      # 🆕 New
├── youtube              # 🆕 New - Fetch transcripts
├── index                # 🆕 New - Generate forge index
├── feedback             # 🆕 New - Feedback management
│   ├── save
│   ├── list
│   ├── stats
│   └── sync
└── --version / --help
```

---

## Package Structure (Updated)

```
src/forge_hooks/
├── __init__.py
├── cli.py                    # Main CLI entry point (update)
├── common/                   # ✅ Existing utilities
│   ├── __init__.py
│   ├── file_discovery.py
│   ├── git_utils.py
│   └── hook_io.py
├── validators/               # ✅ Existing validators
│   ├── __init__.py
│   ├── base.py
│   ├── contains.py
│   ├── new_file.py
│   ├── ownership.py
│   └── marketplace.py        # 🆕 New
├── utils/                    # 🆕 New utilities
│   ├── __init__.py
│   ├── youtube.py            # 🆕 YouTube transcript logic
│   └── indexer.py            # 🆕 Index generation logic
└── feedback/                 # 🆕 New feedback management
    ├── __init__.py
    ├── manager.py            # 🆕 Core feedback operations
    ├── stats.py              # 🆕 Statistics tracking
    └── sync.py               # 🆕 Sync to Product Forge
```

---

## Dependencies (pyproject.toml Update)

```toml
[project]
name = "forge-hooks"
version = "0.2.0"  # Bump version
dependencies = [
    "click>=8.0.0",
]

[project.optional-dependencies]
# Core validation features (always installed with --all-extras)
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
]

# Optional feature groups (install individually)
youtube = [
    "youtube-transcript-api>=0.6.0",
]

marketplace = [
    "jsonschema>=4.0.0",
    "requests>=2.28.0",
]

# Install all optional features
all = [
    "forge-hooks[youtube,marketplace]",
]
```

**Installation options:**
```bash
# Basic install (validators only)
uv tool install .

# With YouTube support
uv tool install .[youtube]

# With marketplace validation
uv tool install .[marketplace]

# With all features
uv tool install .[all]

# Development install
uv sync --all-extras
```

---

## Implementation Phases

### Phase 1: Marketplace Validator (Simplest)
- ✅ No external dependencies beyond jsonschema/requests
- ✅ Fits naturally into existing `validate` command group
- ✅ Quick win to prove the expansion pattern

**Estimated effort:** 1-2 hours

### Phase 2: Forge Index Generator
- ✅ No external dependencies (stdlib only)
- ✅ Self-contained, no complex state
- ✅ Useful for documentation generation

**Estimated effort:** 2-3 hours

### Phase 3: YouTube Transcript Fetcher
- ⚠️ Requires external dependency
- ✅ Self-contained, no complex state
- ✅ High user value for content work

**Estimated effort:** 2-3 hours

### Phase 4: Feedback Manager (Most Complex)
- ✅ No external dependencies
- ⚠️ Stateful (manages learnings directory)
- ⚠️ Multiple subcommands
- ✅ High value for Product Forge workflow

**Estimated effort:** 4-6 hours

---

## Testing Strategy

### Unit Tests

Add test modules:
```
tests/
├── validators/
│   └── test_marketplace.py      # 🆕
├── utils/
│   ├── test_youtube.py          # 🆕
│   └── test_indexer.py          # 🆕
└── feedback/
    ├── test_manager.py          # 🆕
    ├── test_stats.py            # 🆕
    └── test_sync.py             # 🆕
```

### Integration Tests

Update `tests/test_integration.py` with new commands:
- Test marketplace validation with valid/invalid files
- Test index generation with mock plugins directory
- Test YouTube fetcher with mock API responses
- Test feedback save/list/stats workflow

---

## Migration Path

### Scripts to Deprecate (After Migration)

Once all commands are in `forge-hooks`, mark these as deprecated:
- `scripts/fetch-youtube-transcript.py` → Use `forge-hooks youtube`
- `scripts/validate-marketplace.py` → Use `forge-hooks validate marketplace`
- `scripts/generate-forge-index.py` → Use `forge-hooks index`
- `scripts/hooks/save-feedback.py` → Use `forge-hooks feedback save`

Add deprecation notices in each script:
```python
print("DEPRECATED: Use 'forge-hooks <command>' instead", file=sys.stderr)
print("See: forge-hooks --help", file=sys.stderr)
```

### Skill/Hook Updates

Update SKILL.md files and hooks to use new commands:
- Replace Python script paths with `forge-hooks` commands
- Simplify hook configuration (no need for `uv run python scripts/...`)

---

## Benefits

### 1. Unified Interface
- Single command for all Product Forge utilities
- Consistent argument parsing and error handling
- Better discoverability (`forge-hooks --help`)

### 2. Better Distribution
- One package to install: `uv tool install forge-hooks[all]`
- Proper dependency management
- Version-controlled together

### 3. Improved Testing
- Comprehensive test suite for all utilities
- Integration tests across commands
- Better code coverage

### 4. Easier Maintenance
- Shared utilities and helpers
- Consistent coding patterns
- Single point for updates

### 5. Enhanced User Experience
- Tab completion support (future)
- Consistent output formatting
- Better error messages

---

## Success Criteria

### Phase 1 (Marketplace Validator)
- [ ] `forge-hooks validate marketplace` command works
- [ ] Validates against Claude Code schema
- [ ] Tests pass with >80% coverage
- [ ] Documentation updated

### Phase 2 (Forge Index)
- [ ] `forge-hooks index` generates markdown/JSON
- [ ] Scans all plugin types (agents, skills, commands, processes)
- [ ] Tests pass with >80% coverage
- [ ] Output format matches existing generator

### Phase 3 (YouTube)
- [ ] `forge-hooks youtube <url>` fetches transcripts
- [ ] Supports all YouTube URL formats
- [ ] Optional dependency properly configured
- [ ] Tests with mocked API responses

### Phase 4 (Feedback)
- [ ] All feedback subcommands working
- [ ] Backward compatible with existing hooks
- [ ] Statistics tracking accurate
- [ ] Sync command functional

### Final
- [ ] All 4 phases complete
- [ ] Documentation updated (README, DEPLOYMENT_SUMMARY)
- [ ] Deprecation notices in old scripts
- [ ] Version bumped to 0.2.0
- [ ] Published to PyPI (optional)

---

## Next Steps

1. **Review and approve** this plan
2. **Start with Phase 1** (Marketplace Validator) - quick win
3. **Iterate through phases** in order
4. **Update documentation** as we go
5. **Deploy globally** with `uv tool install . --force`

---

**Question for you:** Should we proceed with Phase 1 (Marketplace Validator) first, or would you prefer to tackle a different phase?
