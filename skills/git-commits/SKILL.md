---
name: Git Commit Best Practices
description: Atomic commits, conventional commits, and disciplined version control practices
version: 1.0.0
triggers:
  - git commit
  - commit message
  - atomic commit
  - conventional commit
  - version control
  - commit best practices
---

# Git Commit Best Practices Skill

This skill automatically activates when working with git commits to ensure atomic, well-structured, and meaningful commit history.

## Core Principle

**ATOMIC, CONVENTIONAL, PURPOSEFUL COMMITS**

```
❌ Giant commits mixing features/fixes, vague messages, broken intermediate states
✅ Single-purpose commits, descriptive messages, always buildable codebase
```

## The AFTER Technique

Follow this mnemonic for excellent git hygiene:

```
A - Atomic Commits     → One logical change per commit
F - Frequent Commits   → Commit early and often
T - Test Before Push   → Ensure tests pass before sharing
E - Enforce Standards  → Use conventional commit format
R - Refactoring ≠ Features → Separate refactoring from new code
```

## Atomic Commits

### What Makes a Commit Atomic?

An atomic commit is the **smallest possible, meaningful change** that:

1. **Does exactly one thing** - A single logical unit of change
2. **Leaves codebase working** - All tests pass, code builds
3. **Doesn't mix concerns** - No formatting + logic changes together
4. **Is self-contained** - Can be reverted or cherry-picked independently

### Good vs Bad Commits

```
❌ BAD: "Update user module"
   - Changes authentication logic
   - Fixes a CSS bug
   - Refactors database queries
   - Adds new API endpoint

✅ GOOD: Split into 4 separate commits:
   1. "fix(auth): correct token expiration check"
   2. "fix(ui): align login button on mobile"
   3. "refactor(db): extract user queries to repository"
   4. "feat(api): add user profile endpoint"
```

### Benefits of Atomic Commits

- **Easy to revert** - Roll back one change without losing others
- **Better git bisect** - Find bugs faster with smaller commits
- **Clean cherry-picks** - Move features between branches cleanly
- **Meaningful history** - Understand what changed and why
- **Better code reviews** - Review focused, digestible chunks

## Conventional Commits Format

### Structure

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | Description | SemVer Impact |
|------|-------------|---------------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | - |
| `style` | Code style (formatting, semicolons) | - |
| `refactor` | Code change that neither fixes nor adds | - |
| `perf` | Performance improvement | PATCH |
| `test` | Adding or correcting tests | - |
| `build` | Build system or dependencies | - |
| `ci` | CI configuration | - |
| `chore` | Maintenance tasks | - |
| `revert` | Reverts a previous commit | varies |

### Breaking Changes

Indicate breaking changes with `!` or footer:

```bash
# Using ! notation
feat(api)!: change authentication to OAuth2

# Using footer
feat(api): change authentication to OAuth2

BREAKING CHANGE: API now requires OAuth2 tokens instead of API keys.
Migration guide at docs/migration-v2.md
```

### Examples

```bash
# Feature with scope
feat(auth): add JWT refresh token rotation

# Bug fix
fix(cart): prevent negative quantities on update

# Documentation
docs(api): add rate limiting section to README

# Refactoring
refactor(users): extract validation to separate module

# Performance
perf(search): add database index for email lookups

# Breaking change
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: v1 API endpoints are no longer available.
Migrate to v2 endpoints before upgrading.

# Multiple footers
fix(payment): handle currency conversion edge case

Fixes #234
Reviewed-by: Jane Doe
```

## Commit Message Guidelines

### The Subject Line

```
✅ DO:
- Use imperative mood: "Add feature" not "Added feature"
- Keep under 50 characters (72 max)
- Capitalize first letter after type
- No period at the end
- Be specific: "fix auth timeout" not "fix bug"

❌ DON'T:
- "Fixed stuff"
- "WIP"
- "Updates"
- "Misc changes"
- "Addressing PR feedback"
- Include "Generated with Claude Code" or AI tool attribution
- Include "Co-Authored-By: Claude" or AI co-author footers
- Include 🤖 emoji or any AI generation indicators
```

### The Body (When Needed)

Use the body to explain **what** and **why**, not how:

```bash
fix(api): handle race condition in session creation

The previous implementation could create duplicate sessions
when multiple requests arrived simultaneously. This caused
authentication failures for users with slow connections.

- Add mutex lock around session creation
- Implement idempotency key for requests
- Add retry logic with exponential backoff

Fixes #456
```

### When to Include a Body

- Complex changes needing explanation
- Non-obvious implementation choices
- Changes with broader implications
- Fixes for tricky bugs (explain the root cause)

## Staging Atomic Commits

### Using `git add -p` (Patch Mode)

When a file contains multiple logical changes:

```bash
# Interactive staging - select specific hunks
git add -p

# Commands in patch mode:
# y - stage this hunk
# n - don't stage this hunk
# s - split into smaller hunks
# e - manually edit the hunk
# q - quit
```

### Workflow for Clean History

```bash
# 1. See all changes
git diff

# 2. Stage related changes only
git add -p src/auth.py
git add -p tests/test_auth.py

# 3. Verify staged changes
git diff --staged

# 4. Commit with good message
git commit -m "fix(auth): correct token expiration check"

# 5. Repeat for next logical change
git add -p src/styles.css
git commit -m "fix(ui): align login button on mobile"
```

## Pre-Commit Checklist

Before every commit, verify:

```
📋 Commit Quality Checklist

□ ATOMIC
  □ Single logical change only
  □ No mixed concerns (logic + style + docs)
  □ Could be reverted independently

□ COMPLETE
  □ Code builds successfully
  □ All tests pass
  □ No TODO/FIXME left unaddressed
  □ No debug code or console.log

□ MESSAGE
  □ Uses conventional commit format
  □ Subject under 50 chars (72 max)
  □ Imperative mood ("Add" not "Added")
  □ Body explains why (if needed)

□ CLEAN
  □ No unrelated whitespace changes
  □ No commented-out code
  □ No secrets or credentials
```

## Common Anti-Patterns

### 1. The "Kitchen Sink" Commit

```bash
# ❌ BAD
git add .
git commit -m "Updates"

# ✅ GOOD
# Stage and commit each logical change separately
```

### 2. The "WIP" Commit

```bash
# ❌ BAD
git commit -m "WIP"
git commit -m "WIP again"
git commit -m "Fix WIP"

# ✅ GOOD
# Use branches, then squash or rebase before merging
git rebase -i HEAD~3  # Squash WIP commits
```

### 3. The "Fix Review Comments" Commit

```bash
# ❌ BAD (after code review)
git commit -m "Fix PR comments"
git commit -m "Address feedback"

# ✅ GOOD
# Amend or fixup into the relevant original commit
git commit --fixup <original-commit-hash>
git rebase -i --autosquash main
```

### 4. Mixing Refactoring with Features

```bash
# ❌ BAD
git commit -m "feat: add search and refactor database"

# ✅ GOOD
git commit -m "refactor(db): extract query builder"
git commit -m "feat(search): add full-text search endpoint"
```

## Interactive Rebase for Clean History

Before pushing, clean up your commits:

```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# In the editor:
pick abc1234 feat(auth): add login
squash def5678 fix typo           # Combine with previous
fixup ghi9012 forgot file         # Combine, discard message
pick jkl3456 feat(auth): add logout
reword mno7890 feat: add reset    # Edit commit message
```

## Git Hooks for Enforcement

### commit-msg Hook

```bash
#!/bin/bash
# .git/hooks/commit-msg

commit_regex='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?(!)?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Invalid commit message format!"
    echo "Expected: type(scope): description"
    echo "Example: feat(auth): add password reset"
    exit 1
fi
```

### pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run tests
npm test || exit 1

# Check for debug statements
if git diff --cached | grep -E "console\.log|debugger|binding\.pry"; then
    echo "❌ Debug statements found!"
    exit 1
fi

# Check for secrets
if git diff --cached | grep -E "API_KEY|SECRET|PASSWORD"; then
    echo "❌ Possible secrets detected!"
    exit 1
fi
```

## Warning Triggers

Automatically warn when:

1. **Large diff detected**
   > "⚠️ GIT: This commit has 500+ lines. Consider splitting into atomic commits."

2. **Mixed file types**
   > "⚠️ GIT: Commit includes .py, .css, and .md files. Ensure this is one logical change."

3. **Vague message**
   > "⚠️ GIT: Commit message 'fix bug' is too vague. Be specific about what was fixed."

4. **Missing type prefix**
   > "⚠️ GIT: Use conventional commit format: type(scope): description"

5. **Tests not included**
   > "⚠️ GIT: Feature commit without test changes. Consider adding tests."

Sources:
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- [Atomic Commits Explained](https://www.phparch.com/2025/06/atomic-commits-explained-stop-writing-useless-git-messages/)
- [Git Commit Best Practices](https://www.pullchecklist.com/posts/git-commit-best-practices)
- [Advanced Git Guide - Atomic Commits](https://medium.com/@krystalcampioni/advanced-git-guide-part-1-mastering-atomic-commits-and-enforcing-conventional-commits-1be401467a92)
