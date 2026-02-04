---
name: create-qa-test
description: Create a new QA test procedure for a feature
argument-hint: "<feature-name> [--url <url>] [--priority <priority>]"
---

# create-qa-test

**Category**: Quality Assurance

## Usage

```bash
create-qa-test <feature-name> [--url <url>] [--priority <priority>] [--explore]
```

## Arguments

- `<feature-name>`: Required - Name of the feature to test (kebab-case)
- `--url`: Optional - Test environment URL for the feature
- `--priority`: Optional - Test priority (critical, high, medium, low). Default: medium
- `--explore`: Optional - Launch qa-tester agent to explore the feature via Playwright

## Execution Instructions for Claude Code

When this command is run, Claude Code should:

1. **Generate Test ID**
   - Format: `QA-YYYYMMDD-###-feature-name.md`
   - Use today's date
   - Find next sequential number for today

2. **Create Directory Structure** (if not exists)
   ```
   qa-tests/
   ├── draft/
   ├── active/
   ├── executed/
   ├── archived/
   └── screenshots/
   ```

3. **Prompt for Details** (if not provided)
   - Feature description
   - Test URL (if --url not specified)
   - Acceptance criteria
   - Prerequisites
   - Test data requirements

4. **Create QA Test File**
   - Place in `qa-tests/draft/` with status DRAFT
   - Include all required metadata
   - Generate test case placeholders based on feature

5. **Optional: Invoke qa-tester Agent**
   - If `--explore` flag is set, launch the qa-tester agent
   - Agent will navigate to URL and document test steps
   - Agent will take screenshots of key states

## File Template

```markdown
# QA Test Procedure: [Feature Name]

## Metadata
- **Test ID**: QA-YYYYMMDD-###
- **Feature**: [Feature name]
- **Application**: [App name]
- **URL**: [Test environment URL]
- **Created**: [YYYY-MM-DD]
- **Author**: [Name]
- **Status**: DRAFT
- **Priority**: [Critical|High|Medium|Low]
- **Estimated Time**: [X minutes]
- **PRD Reference**: [Link if applicable]

## Prerequisites
- [ ] [Required setup step 1]
- [ ] [Test account with appropriate permissions]
- [ ] [Test data prepared]

## Test Environment
- **URL**: [Test environment URL]
- **Browser**: Chrome (latest)
- **Credentials**: See password manager

---

## Test Cases

### TC-001: [Happy Path - Main Success Scenario]

**Objective**: Verify the main success flow for [feature]

**Preconditions**:
- User is logged in
- [Feature-specific preconditions]

#### Steps

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Navigate to [URL] | [Page loads correctly] | ☐ | |
| 2 | [Action] | [Expected outcome] | ☐ | |
| 3 | [Action] | [Expected outcome] | ☐ | |

**Postconditions**: [Expected state after test]

---

### TC-002: [Validation Test]

**Objective**: Verify input validation for [feature]

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | [Submit with empty required field] | [Error message appears] | ☐ | |
| 2 | [Enter invalid format] | [Validation error shown] | ☐ | |

---

## Edge Cases & Error Scenarios

### EC-001: [Edge Case Description]

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | [Edge case action] | [Expected behavior] | ☐ | |

---

## Summary Checklist

### Critical Path
- [ ] TC-001: [Title]

### Validation
- [ ] TC-002: [Title]

### Edge Cases
- [ ] EC-001: [Title]

---

## Test Execution Log

| Date | Tester | Environment | Build | Result | Issues |
|------|--------|-------------|-------|--------|--------|
| | | | | | |

## Notes
- [Additional observations]
- [Known limitations]
```

## Example

```bash
# Create a basic QA test for login
create-qa-test user-login --url https://staging.example.com/login --priority critical

# Create a test and explore with Playwright
create-qa-test checkout-flow --url https://staging.example.com/checkout --explore

# Create a simple test, will prompt for URL
create-qa-test password-reset
```

## Output

```
Created: qa-tests/draft/QA-20250105-001-user-login.md

📋 QA Test Procedure: user-login
   Status: DRAFT
   Priority: Critical
   Location: qa-tests/draft/

Next steps:
1. Review and complete test cases
2. Add specific test data
3. Move to qa-tests/active/ when ready
```

## Integration with qa-tester Agent

When `--explore` flag is used:

1. Command creates the initial QA test file
2. Launches qa-tester agent with:
   - Feature name
   - URL to test
   - Path to QA test file
3. Agent navigates and documents steps
4. Agent takes screenshots to `qa-tests/screenshots/{test-id}/`
5. Agent extracts element screenshots to `qa-tests/screenshots/{test-id}/elements/`
6. Agent updates the QA test file with discovered steps
7. **Agent validates and embeds all screenshots** (see Final Review below)

## Final Review: Screenshot Integration (REQUIRED)

**Before marking the QA test as complete, the agent MUST verify all screenshots are properly referenced in the final markdown file.**

### Verification Checklist

1. **Check screenshot directory exists**
   ```
   qa-tests/screenshots/{test-id}/
   ├── 01-initial-state.png
   ├── 02-form-filled.png
   ├── 03-success-state.png
   └── elements/
       ├── login-button.png
       ├── email-field.png
       └── password-field.png
   ```

2. **Verify all screenshots are referenced in the markdown**
   - Each test case should have a "Screenshots" subsection
   - Element references should use relative paths
   - No orphaned screenshots (captured but not referenced)

3. **Add missing references**
   If screenshots exist but aren't in the document, add them:

### Required Sections in Final Document

#### Screenshots Reference (per test case)

```markdown
### TC-001: User Login

#### Steps
| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Navigate to login page | Login form displays | ☐ | |
| 2 | Enter email in **Email field** | Email accepted | ☐ | |
| 3 | Click **Login button** | Dashboard loads | ☐ | |

#### Screenshots
| Step | Screenshot | Description |
|------|------------|-------------|
| 1 | ![Initial state](./screenshots/{test-id}/01-initial-state.png) | Login page before input |
| 3 | ![Success](./screenshots/{test-id}/03-success-state.png) | Dashboard after login |
```

#### Element Visual Reference (document level)

```markdown
## Element Visual Reference

| Element | Screenshot | Selector | Test Case |
|---------|------------|----------|-----------|
| Email field | ![](./screenshots/{test-id}/elements/email-field.png) | `input#email` | TC-001 |
| Login button | ![](./screenshots/{test-id}/elements/login-button.png) | `button[type=submit]` | TC-001 |
```

### Validation Steps

The agent should run these checks before completing:

```
1. LIST all files in qa-tests/screenshots/{test-id}/
2. SCAN the QA test markdown for image references
3. COMPARE: Are all screenshots referenced?
4. IF missing references:
   - Add Screenshots section to each test case
   - Add Element Visual Reference section
   - Use relative paths: ./screenshots/{test-id}/filename.png
5. VERIFY: All image paths are valid (files exist)
6. REPORT: "✅ All X screenshots properly referenced" or "⚠️ Added Y missing references"
```

### Auto-Fix Missing References

If the agent finds screenshots that aren't referenced:

```markdown
## Auto-Generated Screenshot References

The following screenshots were captured but not initially referenced.
They have been added to the document:

| Screenshot | Added To | Path |
|------------|----------|------|
| 02-form-filled.png | TC-001 Screenshots | ./screenshots/QA-20250105-001/02-form-filled.png |
| submit-button.png | Element Reference | ./screenshots/QA-20250105-001/elements/submit-button.png |
```

## Related Commands

- `list-qa-tests` - List and filter existing QA tests
- `enrich-qa-test` - Add element screenshots to existing test
- `/prd-progress` - Check linked PRD implementation status

## Related Skills

- `qa-screenshot-management` - Screenshot naming and organization
- `qa-element-extraction` - Extract element screenshots from test steps
- `qa-screenshot-validation` - Validate screenshots for layout issues
